# Stage E.0 hypothesis catalog: assembled

> **Stage E.1 figures (lead, 2026-09-24, after the user's decisions U1 to U9; docs/DECISIONS.md;
> every edit in reports/stage_e1_changes.md). These govern over every figure and table below.**
> 53 active members, 158 confirmation trials, projected cumulative N = 58 + 158 = 216.
>
> | Cluster | Active members | Confirmation trials | Change from E.0 |
> |---|---|---|---|
> | K1 | 5 (2 new + 3 ports) | 11 | K1-ml-01 excluded (U6); run only if the user decides after K7 (U3) |
> | K2 | 8 (5 new + 3 ports) | 44 | K2-ml-01 excluded (U6); first cluster (U3) |
> | K3 | 9 (6 new + 3 ports) | 31 | K3-ml-01 excluded (U6) |
> | K4 | 8 (5 new + 3 ports) | 19 | K4-ml-01 excluded (U6) |
> | K5 | 7 (4 new + 3 ports) | 16 | K5-ml-01 excluded (U6); platinum OUT (U2): -1 trial each on K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-ovr-01 |
> | K6 | 7 (4 new + 3 ports) | 27 | K6-ml-01 excluded (U6) |
> | K7 | 6 (3 new + 3 ports) | 6 | K7-ml-01 excluded (U6) |
> | K8 | 3 (3 new) | 4 | K8-ml-01 excluded (U6); last cluster (U3) |
> | **Total** | **53** | **158** (93 port + 65 new + 0 ML) | |
>
> Arithmetic: E.0's post-review catalog had 61 members and 170 trials. U6 excludes the eight
> K#-ml-01 members (-8 members, -8 trials). U2 removes platinum from four members (-4 trials, no
> member lost). 61 - 8 = 53; 170 - 8 - 4 = 158; N = 58 + 158 = 216. The ML grid configurations (E.0:
> 384) no longer exist. The per-exposure table below still lists platinum and the ML members: both
> are superseded (reports/stage_e0_catalog.json carries the E.1 figures).
>
> **Post-review figures (lead, Task 8, 2026-09-24 06:21 PDT):** 61 active members, 170 confirmation trials, projected cumulative N = 58 + 170 = 228. K4-ngrev-01 excluded on review R-06; 15 members labelled SOURCE-OVERLAP on review R-04; every ruling is a bracketed note in the entry it changes (reports/stage_e0_review_rulings.md). The summary tables below were assembled before Task 8 and are superseded where they differ.

2026-09-24, assembled by CatalogAssembler-SonnetMed from the eight cluster catalogs
(reports/stage_e0_catalog_K1.md through stage_e0_catalog_K8.md); no entry edited.

**Rule that governs this assembly.** Where a catalog entry carries a bracketed lead ruling
(`[EXCLUDED by the lead, ...]`, `[Narrowed by the lead, ...]`, `[REMOVED by the lead, ...]`,
`[Lead ruling, ...]` or `[Amended by the lead, ...]`), that ruling governs over the writer's
original text and over the catalog's own header/trial-count-table totals wherever they disagree.
Where a catalog's own trial-count table was amended by the lead, the amended row governs; where a
catalog's own header total was not updated to match an amended row, the amended row (not the
header total) is used everywhere in this document's counts, and the mismatch is logged under
"Consistency flags" below.

**How the numbers below were produced.** A small python script
(`/tmp/.../scratchpad/build_catalog.py`, transcribed from a manual, line-by-line read of each
catalog's Section 0 header, Section 1 members, Section 2 excluded-members table and Section 6
trial-count table) tabulates, per member: cluster, type (port/new/ml), exposures traded, trials in
N, active/excluded-by-lead status, starred products traded, source-overlap flag, lead-ruling text
and whether the member's main source is abstract-only. Row counts were checked against
`grep -c "^### K"` (member headers) and `grep -c "^| X-"` inside each catalog's "## 2. Excluded
members" table (writer-excluded candidates) for every file. Commands run and their output:

```
grep -hn "^### K" reports/stage_e0_catalog_K*.md | sed -E 's/.*(K[0-9]+-[a-z0-9]+-[0-9]+).*/\1/' \
  | sort | uniq -c | awk '$1>1'          # -> no output: no duplicate member ids
grep -hc "^### K" reports/stage_e0_catalog_K*.md
  # K1=7 K2=9 K3=10 K4=10 K5=8 K6=9 K7=7 K8=4   (total 64 member headers)
awk '/^## 2\. Excluded members/{flag=1;next}/^## 3\./{flag=0}flag' <file> | grep -c "^| X-"
  # K1=21 K2=9 K3=16 K4=19 K5=17 K6=18 K7=18 K8=14   (total 132 writer-excluded candidates)
```

All 64 member headers are unique; all 64 have a matching Section 6 trial-count-table row (including
the two members excluded by the lead, K1-predrift-01 and K6-ovr-01, which appear in their tables at
0 trials); no table row lacks a matching Members-section entry.

---

## Summary table per cluster

| Cluster | Members active (new / port / ML) | Members excluded by the lead | Candidates excluded by the writer | Confirmation trials (lead amendments applied) | Exposures traded |
|---|---|---|---|---|---|
| K1 | 6 (2 new + 3 port + 1 ML) | 1 (K1-predrift-01) | 21 | 12 | Nasdaq-100, Russell 2000, Dow |
| K2 | 9 (5 new + 3 port + 1 ML) | 0 | 9 | 45 | ZT, ZF, ZN, TN, ZB, UB |
| K3 | 10 (6 new + 3 port + 1 ML) | 0 | 16 | 32 | EUR, AUD, GBP, CAD, JPY, CHF, NZD |
| K4 | 10 (6 new + 3 port + 1 ML) | 0 | 19 | 21 | crude, gas, RBOB, ULSD |
| K5 | 8 (4 new + 3 port + 1 ML) | 0 | 17 | 21 | gold, silver, copper, platinum |
| K6 | 8 (4 new + 3 port + 1 ML) | 1 (K6-ovr-01) | 18 | 28 | ZC, ZW, ZS, ZM, ZL, HE, LE |
| K7 | 7 (3 new + 3 port + 1 ML) | 0 | 18 | 7 | bitcoin |
| K8 | 4 (3 new + 1 ML; no ports) | 0 | 14 | 5 | gold, CAD, Nasdaq-100 (traded legs) |
| **Total** | **62** | **2** | **132** | **171** | |

Note: "Confirmation trials" is the sum of Section 6 trial-count-table rows for that cluster's
active members, with every lead amendment applied at the row level. Three clusters' own stated
cluster-total figure (in their Section 0 header and at the foot of their Section 6 table) is stale
relative to this row sum; see "Consistency flags" below (K3: stated 36, actual 32; K5: stated 22,
actual 21; K6: stated 39, actual 28). A fourth, K1, has the same issue (stated 13, actual 12).

---

## Per-exposure table

Exposure, cluster, the member ids trading it (active members only), and the summed trial count on
it (from Section 6 rows, split evenly across a member's traded exposures where a member trades more
than one; every K1-K8 member happens to carry exactly 1 trial per exposure it trades, except the
ML members, whose 1 confirmation trial sits on their single named vehicle exposure, and
K8-flight-01, whose 2 trials — H30 and HEOD exit variants — both sit on gold).

| Cluster | Exposure | Member ids | Trials on this exposure |
|---|---|---|---|
| K1 | Dow | K1-cp1-01, K1-cp2-01, K1-cp3-01 | 3 |
| K1 | Nasdaq-100 | K1-cp1-01, K1-cp2-01, K1-cp3-01, K1-vxnband-01, K1-vwap-01, K1-ml-01 | 6 |
| K1 | Russell 2000 | K1-cp1-01, K1-cp2-01, K1-cp3-01 | 3 |
| K2 | TN | K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-monthend-01 | 7 |
| K2 | UB | K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-monthend-01 | 7 |
| K2 | ZB | K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-predrift-01, K2-monthend-01 | 8 |
| K2 | ZF | K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-monthend-01 | 7 |
| K2 | ZN | K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-predrift-01, K2-monthend-01, K2-ml-01 | 9 |
| K2 | ZT | K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-monthend-01 | 7 |
| K3 | AUD | K3-cp1-01, K3-cp2-01, K3-cp3-01 | 3 |
| K3 | CAD | K3-cp1-01, K3-cp2-01, K3-cp3-01 | 3 |
| K3 | CHF | K3-cp1-01, K3-cp2-01, K3-cp3-01, K3-ldnrev-01 | 4 |
| K3 | EUR | K3-cp1-01, K3-cp2-01, K3-cp3-01, K3-ldnrev-01, K3-ldnmom-01, K3-mehedge-01, K3-ecbfix-01, K3-ml-01 | 8 |
| K3 | GBP | K3-cp1-01, K3-cp2-01, K3-cp3-01 | 3 |
| K3 | JPY | K3-cp1-01, K3-cp2-01, K3-cp3-01, K3-ldnrev-01, K3-ldnmom-01, K3-mehedge-01, K3-tkypre-01, K3-tkypost-01 | 8 |
| K3 | NZD | K3-cp1-01, K3-cp2-01, K3-cp3-01 | 3 |
| K4 | RBOB | K4-cp1-01, K4-cp2-01, K4-cp3-01 | 3 |
| K4 | ULSD | K4-cp1-01, K4-cp2-01, K4-cp3-01, K4-ovr-01 | 4 |
| K4 | crude | K4-cp1-01, K4-cp2-01, K4-cp3-01, K4-apipre-01, K4-eiafade-01, K4-eiamom-01, K4-ovr-01, K4-ml-01 | 8 |
| K4 | gas | K4-cp1-01, K4-cp2-01, K4-cp3-01, K4-ngpre-01, K4-ngrev-01, K4-ovr-01 | 6 |
| K5 | copper | K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-ovr-01 | 4 |
| K5 | gold | K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-preauc-01, K5-pmfix-01, K5-fomc-01, K5-ovr-01, K5-ml-01 | 8 |
| K5 | platinum | K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-ovr-01 | 4 |
| K5 | silver | K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-preauc-01, K5-ovr-01 | 5 |
| K6 | HE | K6-cp1-01, K6-cp2-01, K6-cp3-01, K6-limitcont-01 | 4 |
| K6 | LE | K6-cp1-01, K6-cp2-01, K6-cp3-01, K6-limitcont-01 | 4 |
| K6 | ZC | K6-cp1-01, K6-cp2-01, K6-cp3-01, K6-wasdepre-01, K6-wasdepost-01, K6-ml-01 | 6 |
| K6 | ZL | K6-cp1-01, K6-cp2-01, K6-cp3-01 | 3 |
| K6 | ZM | K6-cp1-01, K6-cp2-01, K6-cp3-01 | 3 |
| K6 | ZS | K6-cp1-01, K6-cp2-01, K6-cp3-01, K6-crushgap-01, K6-wasdepre-01 | 5 |
| K6 | ZW | K6-cp1-01, K6-cp2-01, K6-cp3-01 | 3 |
| K7 | bitcoin | K7-cp1-01, K7-cp2-01, K7-cp3-01, K7-expiry-01, K7-rev2h-01, K7-montrend-01, K7-ml-01 | 7 |
| K8 | CAD | K8-oilcad-01, K8-ml-01 | 2 |
| K8 | Nasdaq-100 | K8-wkndbtc-01 | 1 |
| K8 | gold | K8-flight-01 | 2 |

---

## Totals

- **Active members (all 8 clusters): 62** (of 64 member entries written; 2 excluded by the lead:
  K1-predrift-01, K6-ovr-01).
- **Confirmation trials (Stage E, all clusters): 171** (sum of the "Confirmation trials" column
  above: 12 + 45 + 32 + 21 + 21 + 28 + 7 + 5 = 171).
- **ML screening-grid configurations: 384** (48 per ML member x 8 ML members, one per cluster:
  K1-ml-01, K2-ml-01, K3-ml-01, K4-ml-01, K5-ml-01, K6-ml-01, K7-ml-01, K8-ml-01). This is a
  research-window accounting figure under design D15.8 and is **NOT added to N**; each ML member
  contributes exactly 1 trial to the confirmation-trial totals above, already counted there.

## Projected cumulative N

```
N before Stage E (program, after Stage D.1f)  =  58
+ Stage E confirmation trials (all 8 clusters) = 171
--------------------------------------------------------
Projected cumulative N after Stage E           = 229
```

This projection assumes D2 admits every exposure named in every active member's header (the
"all exposures admitted" case each catalog's Section 6 table states). If D2 excludes any exposure
in E.2, the actual Stage E trial count, and so the projected N, will be lower; each catalog gives
the general per-exposure formula in its own Section 6.

---

## Consistency flags

1. **K1** — Section 0 header and the foot of Section 6's trial-count table both state the cluster
   total as **13** (9 port + 3 new + 1 ML). Summing the Section 6 table's own member rows after the
   lead's 02:15 PDT 2026-09-24 exclusion of K1-predrift-01 (row value 0, not 1) gives 9 port + 2 new
   + 1 ML = **12**. The "3 new" figure (vxnband 1 + vwap 1 + predrift 1 = 3) is the pre-exclusion
   count and was not revised after the ruling. This report uses 12.
2. **K3** — Section 0 header and the foot of Section 6's table state the cluster total as **36**
   (21 port + 14 new + 1 ML). Summing the table's rows after the lead's 01:40 PDT 2026-09-24
   narrowing of K3-ldnmom-01 (row value 2, not 6) gives 21 port + 10 new + 1 ML = **32**. The
   "14 new" figure (ldnrev 3 + ldnmom 6 + mehedge 2 + ecbfix 1 + tkypre 1 + tkypost 1 = 14) is the
   pre-narrowing count. This report uses 32.
3. **K5** — Section 0 header and the foot of Section 6's table state the cluster total as **22**
   (12 port + 9 new + 1 ML). Summing the table's rows after the lead's 01:47 PDT 2026-09-24 removal
   of the platinum leg from K5-preauc-01 (row value 2, not 3) gives 12 port + 8 new + 1 ML = **21**.
   The "9 new" figure (preauc 3 + pmfix 1 + fomc 1 + ovr 4 = 9) is the pre-removal count. This
   report uses 21.
4. **K6** — Section 0 header and the foot of Section 6's table state the cluster total as **39**
   (21 port + 17 new + 1 ML). Summing the table's rows after all three of the lead's 01:52 PDT
   2026-09-24 rulings (K6-crushgap-01 narrowed to 1, K6-limitcont-01 narrowed to 2, K6-ovr-01
   excluded to 0) gives 21 port + 6 new + 1 ML = **28**. The catalog's own Section 6 note anticipates
   this ("The cuts in section 7, item 7 would bring it to 28"), which corroborates 28 as the correct
   post-ruling figure; 39 is the pre-ruling figure and was not revised in the header or the table's
   own total line. This report uses 28.
5. **K2, K4, K7, K8** — no mismatch found: each cluster's stated header/table total equals the sum
   of its own Section 6 rows (K2 45=45, K4 21=21, K7 7=7, K8 5=5).
6. **Duplicate member ids** — none. `grep -hn "^### K" reports/stage_e0_catalog_K*.md | sed -E
   's/.*(K[0-9]+-[a-z0-9]+-[0-9]+).*/\1/' | sort | uniq -c | awk '$1>1'` returned no rows across all
   64 member headers in the eight files.
7. **Trial-table rows vs. Members-section entries** — every Section 6 row has a matching Section 1
   member entry and vice versa in all eight catalogs, including the two lead-excluded members
   (K1-predrift-01, K6-ovr-01), which are kept in both sections "for the record" at 0 trials, exactly
   as their rulings direct. No orphaned rows or entries found.

---

## Lists

### Members trading a starred product (MNQ, M2K, MYM, M6E, M6A, MCL, MGC, SIL, MBT)

| Member | Starred product(s) |
|---|---|
| K1-cp1-01 | MNQ, M2K, MYM |
| K1-cp2-01 | MNQ, M2K, MYM |
| K1-cp3-01 | MNQ, M2K, MYM |
| K1-vxnband-01 | MNQ |
| K1-vwap-01 | MNQ |
| K1-ml-01 | MNQ |
| K3-cp1-01 | M6E, M6A |
| K3-cp2-01 | M6E, M6A |
| K3-cp3-01 | M6E, M6A |
| K3-ldnrev-01 | M6E |
| K3-ldnmom-01 | M6E |
| K3-mehedge-01 | M6E |
| K3-ecbfix-01 | M6E |
| K3-ml-01 | M6E |
| K4-cp1-01 | MCL |
| K4-cp2-01 | MCL |
| K4-cp3-01 | MCL |
| K4-apipre-01 | MCL |
| K4-eiafade-01 | MCL |
| K4-eiamom-01 | MCL |
| K4-ovr-01 | MCL |
| K4-ml-01 | MCL |
| K5-cp1-01 | MGC, SIL |
| K5-cp2-01 | MGC, SIL |
| K5-cp3-01 | MGC, SIL |
| K5-preauc-01 | MGC, SIL |
| K5-pmfix-01 | MGC |
| K5-fomc-01 | MGC |
| K5-ovr-01 | MGC, SIL |
| K5-ml-01 | MGC |
| K7-cp1-01 | MBT |
| K7-cp2-01 | MBT |
| K7-cp3-01 | MBT |
| K7-expiry-01 | MBT |
| K7-rev2h-01 | MBT |
| K7-montrend-01 | MBT |
| K7-ml-01 | MBT |
| K8-flight-01 | MGC |
| K8-wkndbtc-01 | MNQ |

K1-predrift-01 (excluded by the lead) would have traded MYM; K2 and K6 have no starred products
(neither cluster's Section 0 header names one).

### Members labelled "source-overlap"

- **K8-wkndbtc-01** only. Its own Section 0 header states: "K8-wkndbtc-01 is labelled
  'source-overlap'; no other member is (C15)." No source-overlap label was found on any other
  member across all eight catalogs.

### Members that are abstract-only in their main source (per the catalog's own text)

- **K1-vxnband-01** — main source K1-005 (Seeck 2026) is logged "abstract only" (SSRN returned 403,
  single author); this is the member's only real source.
- **K4-ngrev-01** — main claim is sourced to K4-006, logged "(abstract only)".
- **K5-preauc-01** — "Evidence quality: Abstract only: SSRN blocked, no mirror (K5 log). A
  practitioner working paper, never published."
- **K6-wasdepre-01** — both of its "What is claimed" passages (P-K6-027-a and P-K6-043-a) are logged
  "(WASDE, abstract only)".
- **K8-flight-01** — "Evidence status: abstract only (K8-003)."
- **K8-wkndbtc-01** — "Evidence status: abstract only, from a 17-page working paper (K8-004)." (also
  labelled source-overlap, above).

Members whose main source is full text, with only a secondary/supporting citation marked "abstract
only" (K1-cp1-01/CP1's siblings via K3-040; K2's K2-aucpre-01 via K2-006 as support; K3-ecbfix-01's
"pit era" context passage; K6-limitcont-01's secondary Park citation; K7-cp1-01's secondary K7-018
citation) are **not** included in this list, since their own governing evidence is not abstract-only.

### Entries amended or excluded by the lead

| Id | Ruling time (PDT, 2026-09-24) | Ruling, first sentence |
|---|---|---|
| K1-predrift-01 | 02:15 | "EXCLUDED by the lead, answering this writer's question 2: this is MES's scheduled-macro-drift family (E-H1/E-H2, class C5, null on MES under docs/NULL_CRITERIA.md) re-run on the Dow, a sibling index highly correlated with the S&P; the K1 brief allows MES families only through the core ports." |
| K2-cp2-01 | 21:12 | "Amended by the lead, to D6's amended CP2 text (entry window bounded at C), answering this writer's note below." |
| K3-ldnmom-01 | 01:40 | "Narrowed by the lead, answering [the writer's question]: traded exposures EUR {6E, E7, M6E}, JPY {6J}." (exposures narrowed from six to two) |
| K5-preauc-01 | 01:47 | "REMOVED by the lead, answering this writer's question 3: one abstract (Nilsson) supports the member, and platinum carries the coverage and 'may be suspended' risks; K5-preauc-01 is kept on gold and silver only, 2 trials." |
| K5-ml-01 | 01:47 | "Lead ruling, question 6: fallback order if D2 does not admit gold: silver, then copper; the features stay as written, reading silver bars (an IN exposure) whether or not silver is traded." |
| K6-crushgap-01 | 01:52 | "Lead ruling, on this writer's question 1: traded on ZS ONLY (1 trial); ZM and ZL removed. The evidence is about the crush spread, and a spread cannot meet the 1-lot cap; the most liquid leg is kept." |
| K6-limitcont-01 | 01:52 | "Lead ruling, question 6: traded on HE and LE ONLY (2 trials); the five grain exposures removed. Its trades are largely a subset of CP3's, so the grain trials add little information." |
| K6-ovr-01 | 01:52 | "EXCLUDED by the lead, question 6: no grain-specific result is logged and one logged source argues against it (K6-025). Moved to the excluded list; 0 trials." |

No lead ruling of any kind was found in K4.md, K7.md or K8.md (`grep -n "EXCLUDED by the lead\|
Narrowed by the lead\|REMOVED by the lead\|Lead ruling\|Amended by the lead"` returned no matches
in those three files).

---


# Cluster K1

# Stage E.0 hypothesis catalog, cluster K1 (equity index: MNQ, NQ, M2K, RTY, MYM, YM)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K1-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K1 runs only if the user decides, after K7, that it is needed; its members stay in the frozen catalog so that a later K1 session is pre-registered.
> **K1 after the decisions: 5 active members, 11 confirmation trials** (2 new + 3 core ports; 9 port + 2 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K1-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from about 01:30 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K1 product existed on this machine.
- The MES bars on disk were not opened. No MES result table was read. The only MES result used is
  the class-level statement in commit ca8befb ("Stage D.1f run, MES classes C1-C5 and C7 null on
  2020-02-03..2024-02-29"), with docs/NULL_CRITERIA.md as the definition of "null".
- Product-specific numbers used: contract specifications and public ADV
  (reports/stage_e0_liquidity.json; the design D1 table), Topstep's fees, hours and rules
  (reports/stage_e0_topstep_facts.md), and event-calendar metadata (ISM release dates and clock
  time).
- No price level, range or volatility of any instrument is used or assumed below, and no VXN or VIX
  value either.

**Inputs read in full:**
- reports/stage_e0_research_K1.md.
- Every `[K1]`-tagged passage in the other logs:
  - K2-007 and K2-015 in reports/stage_e0_research_K2.md;
  - K3-007, K3-030, K3-035 and K3-040 in reports/stage_e0_research_K3.md;
  - the K4-043 and K4-050 entries and the K1-leg flags in reports/stage_e0_research_K4.md;
  - the K8 entries with a K1 leg in reports/stage_e0_research_K8.md.
  - The K5, K6 and K7 logs hold no `[K1]`-tagged passage, only K8 flags. The superseded sonnet
    partial logs were not used.
- reports/stage_e0_source_registry.jsonl (the K1 lines and every line tagged K1).
- The D.1 literature log (432f46d4.../d1/task1_log.md).
- reports/stage_d1f_confirmation_list.md: sections 0 to 2, and 2.1 A3 in full.
- docs/STAGE_E_DESIGN.md (D1-D15, with the amendments of 21:12, 21:52 and 01:40 PDT).
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md: F1 to F6 and F12.
- reports/stage_e0_liquidity.json: the K1 rows.
- MES modules named in D6:
  - strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py;
  - strategy/research/h_daily_bar/h6_prior_close_location.py and _mechanics.py (constants);
  - reports/stage_d1b_family_f_declaration.md F3.3.
- Docstrings only, to check for duplicates: the MES modules e_calendar_event/h1 and h2,
  c_short_horizon_reversal/h1 and d_volatility_state/h1.
- For format only: reports/stage_e0_catalog_K4.md and reports/stage_e0_catalog_K3.md.

**Official pages fetched in this task** (curl, 2026-09-24 01:51-01:58 PDT). Fetches were limited to
confirming data availability and release times. No mechanism research was done and no index value
was downloaded. Saved copies are in the session scratchpad under fetch/, not in the repository.
1. `curl -sI` (headers only, no body) of
   https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv: "HTTP/2 200",
   "content-type: text/csv", "content-length: 218502", "last-modified: Wed, 23 Sep 2026 01:51:09 GMT".
2. `curl -sI` of https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv: "HTTP/2 200",
   "content-type: text/csv", "content-length: 472921", same last-modified.
3. `curl -sI` of https://fred.stlouisfed.org/series/VXNCLS and .../VIXCLS: no status line returned, so
   the FRED copies are **not confirmed**.
4. https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/ redirects to
   an SSO login page, so the calendar could not be read directly.
5. Wayback CDX of that page returned 26 captures, 2020-08-09 to 2026-08-04 (collapsed by month).
   Two were read:
   - http://web.archive.org/web/20260415040000id_/https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/
     says: "The ISM Services PMI® Report is released on the third business day of the month at 10:00
     a.m. (EST)." Its 2026 table lists every month's date, with the footnote "**Services PMI moved
     due to 4th of July holiday observed on July 3, 2026".
   - http://web.archive.org/web/20200809022121id_/https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/
     says: "The Services ISM Report On Business® is released on the third business day of the month
     at 10:00 a.m. (EST)."
6. Wayback CDX of lseg.com/en/ftse-russell/russell-reconstitution*. One capture was read:
   http://web.archive.org/web/20251214041535id_/https://www.lseg.com/en/ftse-russell/russell-reconstitution?kui=pap7J6zdqa-iS3776etidA
   - It says: "Following market consultation, FTSE Russell has announced the reconstitution of the
     Russell US Indexes will change from an annual to a semi-annual schedule in 2026."
   - The lines matched do not name the second 2026 month, so the log's November-against-December
     conflict (K1-018 against K1-023) stays open. No member depends on it.

---

## 0. Header

| Item | Value |
|---|---|
| Products | MNQ*, NQ, M2K*, RTY, MYM*, YM (Topstep F1; * = starred) |
| Exposures IN | Nasdaq-100 {MNQ, NQ}; Russell 2000 {RTY, M2K}; Dow {MYM, YM}. Design D1 table, 2026 Jan-Aug ADV: MNQ 2,363,465, NQ 593,595; RTY 209,871, M2K 115,832; MYM 152,686, YM 108,142. Coverage 1.000 for each exposure |
| **D1 applied: NKD out; S&P leg only** | NKD fails D1(a) (7,969) and D1(b) (0.621), so no member trades or reads it. ES and MES are closed (D1.5). MES bars, already owned, appear only as a signal leg in K1-ml-01, and only on research-window and confirmation-window dates, never holdout dates. No member trades ES or MES |
| Members | **7 = 3 new + 3 core ports + 1 ML member.** The budget is 15 (at most 11 new), so 8 slots are unused (section 3) |
| Trials in N (confirmation) | **13 if D2 admits all three exposures:** 9 port + 3 new + 1 ML. In general 3E + 3a_N + a_D, where E is the number of admitted exposures and a_N, a_D are 1 if the Nasdaq-100 and the Dow are admitted |
| ML grid | ~~48 configurations, counted only in the K1 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Starred products and the rules that apply | **MNQ, M2K, MYM** are starred (F1). Their referent is Topstep's "Risk Adjustments: High Risk/High Volatility" article (F12.1), which names them, and D9.8 encodes it through D9.11 and D9.12. So, unlike M6E and M6A, they stay D2 candidates. **D9.12 CPI window:** opening transactions in [CPI - 5 min, CPI + 5 min] are limited to 3 contracts on MNQ, M2K and MYM, and are not allowed at all on NQ, RTY and YM. CPI is released at 07:30 CT, so the window is 07:25-07:35 CT. No K1 member fills before 08:31 CT, so the window never binds (checked in every entry). **D9.11:** no equity-index position figure is published. The same page says "Trading on mini-sized contracts or larger may be temporarily halted for affected products" (F12.1), a deployability risk if D2 picks NQ, RTY or YM (section 7) |
| D2 | Every entry says "D2 (chosen in E.2)". Within each exposure, the micro and the mini quote the same index in the same tick size in points (C7), so a rule makes the same decisions on either vehicle; only size, cost and tick value differ. Every entry is **traded only if D2 admits the exposure** |

### Common conventions (they apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.**
  - Times are America/Chicago (CT).
  - "The bar at hh:mm" is the ohlcv-1m bar whose ts_event (its open) is hh:mm:00 CT (D.1f
    convention H-8). It closes at hh:mm + 1 min, and its values are usable from then on.
  - Eastern-time releases convert to CT by subtracting one hour; both zones change clocks on the
    same dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine
  convention D6 and D15.3 use).
- **C3 Trade date.** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md, line 40). "The
  trade date's first bar" is the 17:00 CT bar of d-1 (Sunday's for a Monday).
- **C4 Exclusions for the three new members.** The ports follow D6 as written. A new member does
  not trade on:
  - roll-blackout dates ("The splice trade date plus the 2 sessions before it", docs/SCREENING.md);
  - dates that the D10 equity calendar marks as an early close or early halt (Family H: "Days with
    early_halt_ct set: no trade");
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which the bars of one
    computation or one position carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
  flatten at F is the backstop.
- **C5 Flat time.**
  - F = 15:08 CT (D9.1). D6 equity row: O = 08:30, C = 15:00, F = 15:08.
  - No new member's last fill is later than 14:59 CT; K1-ml-01's is 14:35.
  - Early-close days: F = the early close minus 15 minutes (D9.1; F12.3: "Close all positions 15
    minutes before early close"). The new members do not trade on those days (C4).
- **C6 Size.** q_c of the exposure's D2 vehicle, at most 1 lot-equivalent (D2; D9.5).
  - Micros count 0.1 and minis 1 (D9.6), so q_c <= 10 on a micro and q_c = 1 on a mini.
  - No member sizes by signal.
- **C7 Ticks, fees and rulebook chapters.**
  - Sources: tick size, tick value and rulebook chapter from reports/stage_e0_liquidity.json (CME
    contract specifications, fetched 2026-09-23 20:41-20:42 PDT); round turns from Topstep F3.

  | Contract | Exposure | Tick (index points) | Tick value | Topstep round turn | Lot-equivalent | Rulebook |
  |---|---|---|---|---|---|---|
  | MNQ* | Nasdaq-100 | 0.25 | $0.50 | $1.22 | 0.1 | CME 361 |
  | NQ | Nasdaq-100 | 0.25 | $5.00 | $3.78 | 1 | CME 359 |
  | M2K* | Russell 2000 | 0.10 | $0.50 | $1.22 | 0.1 | CME 363 |
  | RTY | Russell 2000 | 0.10 | $5.00 | $3.78 | 1 | CME 393 |
  | MYM* | Dow | 1.0 | $0.50 | $1.22 | 0.1 | CBOT 28 |
  | YM | Dow | 1.00 | $5.00 | $3.78 | 1 | CBOT 27 |

  - These are 2026 specifications. E.2 confirms that each tick was unchanged over 2019-05..2026-06
    before any bar is read, because CP2's buffer and several ML features are in ticks.
- **C8 Price data.**
  - Source: Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is bought
    in E.1, and the confirmation and holdout-2 history of the chosen vehicle in E.2b (D13).
  - Listing dates (liquidity JSON): MNQ, M2K and MYM 2019-05-06 (CME press release: "announced the
    successful launch of its new Micro E-mini futures"); NQ 1999-06-21; RTY 2017-07-10 (a
    planned-date announcement); YM 2002-04 (month only).
  - D2 and D4 let E.2 declare the full-size contract's bars as the price path of a micro vehicle.
  - A bar is available at its close (C1).
  - Every new-member rule compares prices as percentages, signs or VWAP deviations, so it decides
    the same way on either contract of an exposure. Tick-denominated quantities appear only in CP2's
    buffer and in the ML features.
- **C9 External data read by any K1 member** (other than the vehicle's own bars):
  - **VXN** (Cboe Nasdaq-100 Volatility Index), daily close.
    - Source: Cboe's public daily file (fetch 1: HTTP 200, text/csv, 218,502 bytes). It is free.
    - E.2 confirms, when it builds the input, that the file covers 2019-04-30..2026-06-18 (every
      trade date before a research or confirmation date). The file size implies thousands of
      daily rows [inference]; no row was read.
    - FRED VXNCLS is a possible second copy, not confirmed (fetch 3).
    - Availability: the close of trade date d-1 is used only from 08:30 CT on d. Cboe's exact
      publication time is [unverified]; E.2 confirms it.
    - Used by K1-vxnband-01 and K1-ml-01.
  - **ISM Services (formerly Non-Manufacturing) PMI release calendar.** Dates and clock time only;
    no released value is read.
    - Source: ISM's "Report Release Date Calendar" (fetch 4-5). It is free through Wayback: 26
      captures, 2020-08-09..2026-08-04.
    - The tables for 2019-05..2020-07 are not confirmed in E.0. E.2 sources them, for example from
      captures of ISM's earlier URL or from ISM's press-release record.
    - Rule: "released on the third business day of the month at 10:00 a.m. (EST)". The page writes
      "(EST)" year-round; it is read as US Eastern clock time [inference], that is 09:00 CT. E.2
      confirms this against actual publication times.
    - Each year's table is published ahead of the year: the 2026-04-15 capture already lists every
      2026 date through December.
    - Used by K1-predrift-01. The rename from "Non-Manufacturing" to "Services" is taken to be the
      same report [inference: the 2020 capture already says "Services ISM Report On Business"; the
      source paper uses the Non-Manufacturing name for 2008-2014]. E.2 confirms the continuity.
  - **MES ohlcv-1m bars**: owned; built in D.1f for the research window (2025-04-01..2026-06-19) and
    the confirmation window (2019-05..2024-02). Used only by K1-ml-01, never on a holdout date.
    Not opened in E.0.
  - **The Russell 2000 vehicle's bars** (or the price path declared for it): paid, as in C8. Used
    only by K1-ml-01.
  - **Not read by any member.** Their availability is stated here because the brief's rule 3 asks
    for it:
    - VIX daily: Cboe's public file, free (fetch 2).
    - Cash-index levels (Nasdaq-100, Russell 2000, DJIA): no member needs them. Every member uses
      the futures' own bars. A free intraday history was not searched for in E.0 [not checked].
    - Index reconstitution calendars:
      - FTSE Russell publishes its schedule in advance (the lseg.com reconstitution page, fetch 6;
        P-K1-018-c gives the 2025 rank day and effective date). The Nov-Dec 2026 conflict is open.
      - Nasdaq-100 reconstitution dates follow Nasdaq's index methodology, which was not fetched.
      - No member uses either calendar (X-03, X-04). Were one ever used, its dates must come from
        these published schedules, never from volume.
    - NYSE closing-auction imbalance messages (K1-024): paid Databento US Equities data, not in the
      spend plan; the history start is not confirmed. Not used (X-05).
- **C10 Releases inside the K1 session.**
  - Topstep's release table (F6) has "Unemployment Rate | 7:30 AM | ES, NKD, NQ, ... YM, ... RTY,
    ..." (before the 08:30 open, so no K1 fill can meet it) and "FOMC Statement | 1:00 PM | All
    products".
  - K1-predrift-01 names the ISM Services release at 09:00 CT for the Dow exposure. The D9.5a guard
    and the D8 event-window cost therefore apply to the Dow at [09:00, 09:02) and [09:00, 09:30).
  - D9.5a event-minute fill guard: any K1 fill that would land in [13:00, 13:02) on a scheduled FOMC
    day fills at the 13:02 open. The same holds at [09:00, 09:02) on ISM Services days for the Dow.
  - D8 event-window cost: fills in [13:00, 13:30) on FOMC days pay the largest s_b of the product's
    buckets. So do Dow fills in [09:00, 09:30) on ISM Services days.
  - Whether ISM Services also concerns NQ and RTY (for the guard and the cost) is the lead's
    decision (section 7, item 6).
  - CPI: D9.12, as in the header; it never binds.
- **C11 Price-limit proximity (D9.7).**
  - Topstep F12.1: "Equity products ES, MES, NQ, MNQ, RTY, M2K, YM, and MYM overnight price limits
    have expanded from 5% to 7%".
  - E.2 builds the K1 limit tables from the rulebook chapters in C7: the overnight and
    regular-hours limits, their reference prices, and their 2019-2026 history.
  - Every K1 member obeys the encoded rule: no entry, and an immediate exit, while the price is
    within 2% of the day's limit price. No K1 rule reads a limit.
- **C12 Frequency (arithmetic from calendar counts only).**
  - The research window 2025-04-01..2026-06-19 has 319 weekdays (about 305 CME trade dates).
  - The confirmation window from the earliest S_X (2019-05-06) to 2024-02-29 has 1,259 weekdays.
  - The equity-index quarterly roll blacks out about 12 trade dates a year (4 rolls x 3 dates).

---

## 1. Members

### K1-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K1. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures** (each a separate trial, each traded only if D2 admits it): Nasdaq-100
  {MNQ, NQ}, Russell 2000 {RTY, M2K}, Dow {MYM, YM}. **Vehicle:** D2 (chosen in E.2).
- **Session constants** (D6 equity row): O = 08:30, C = 15:00, F = 15:08 CT.
- **Mechanism:** port of MES F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log A10
  and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the
    trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open),
    in the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or
    after C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else
    no trade."
  - **Covered by CP1.** D.1 A10 (Baltussen, Da, Lammers, Martens) is on-instrument for NQ ("Directly
    on-instrument (S&P E-mini, NQ)", D.1 log row A10; cited by the K1 log's header, not re-read).
    Three K1-log rejections are this family: R-K1-067 (Shum et al., LETF close hedging, "the LETF
    close-hedging mechanism is D.1 A10's"), R-K1-068 (Rosa 2022, "D.1 A10/A28 family, generic") and
    R-K1-069 (Baltussen et al. 2021, "see D.1 A10").
  - **Conflicting evidence:** K3-040 (Kosowski et al., "Overnight-Intraday Reversal Everywhere",
    registry-tagged K1; title only, content [unverified]) says the overnight return reverses
    intraday. That is the opposite sign to CP1's (a) form, whose signal is mostly the overnight
    move.
- **MES record:** the same family was null on MES. docs/NULL_CRITERIA.md defines the statement; the
  D.1f result is commit ca8befb, "MES classes C1-C5 and C7 null on 2020-02-03..2024-02-29", and
  F3.3 is class C3. The sibling indices are highly correlated with the S&P (the lead's note; no
  correlation figure is logged or computed here), so these three trials are close to the MES record.
- **Instantiated:**
  - **Signal:** close of the bar at 08:59 minus the open of the trade date's first bar (the 17:00 CT
    bar of d-1, C3).
  - **Entry:** market intent on the bar at 14:29 in the signal's direction, filling at the 14:30
    open. A zero signal means no trade.
  - **Exit:** market intent on the first bar at or after 14:58, filling at the 14:59 open.
  - **Holding horizon:** 29 minutes. **Session window:** 14:30-14:59 CT. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8; paid; history
  2019-05..2026-06). The latest signal input, the 08:59 bar, is available at 09:00 CT.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (C6).
- **Parameters:** O+29 = 08:59, C-31 = 14:29, C-2 = 14:58 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes.
  Floor: at most 20 entries a day, ok; 2-minute minimum hold, ok; 10-minute mean hold, ok.
- **Falsification:** the standard condition only (a port; D6 is unchanged). UCB95 of the member's
  mean net daily P&L per contract below eps_X, at >= 80% achieved null power on the confirmation
  window, counts against it.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills.
  4. Star rules (D9.8, D9.12): MNQ, M2K and MYM are starred. The CPI window is never touched (fills
     at 14:30 and 14:59). D9.11 has no equity figure. The mini-halt note applies if D2 picks a mini.
  5. News: 1 lot-equivalent at most. No Topstep-table release falls in 14:30-14:59.
  6. Event-minute guard: no fill can land in [13:00, 13:02) or [09:00, 09:02).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:** ohlcv-1m of each admitted K1 vehicle over the research window 2025-04-01..2026-06-19
  and the confirmation window S_X..2024-02-29 (D4), including the 17:00 CT reopen bar that the signal
  reads. No external data.
- **Trials in N:** 3 (one per admitted exposure).

### K1-cp2-01 (core port CP2, opening-range breakout)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP on the Nasdaq-100 trial: the 75-minute hold came from Mesfin's MNQ result (D.1 B5), whose sample window is not recorded; treated as overlapping until E.1 records it.]
- **Cluster** K1. **Products read:** own vehicle.
- **Exposures:** Nasdaq-100, Russell 2000, Dow, one trial each, each traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Session constants:** O = 08:30, C = 15:00, F = 15:08 CT.
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py,
  hold_minutes = 75), as fixed in D6 row CP2 with the 21:12 amendment and the 21:52 buffer ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first
    bar opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P;
    market intent in the break direction; one entry per trade date; no entry from C on. Exit: 75
    minutes after the fill, or the engine's forced flatten at F if earlier." The ruling adds: "'4
    ticks of P' in CP2 means 4 minimum price increments of the exposure's most active contract (D1
    table), in price units, fixed whatever vehicle D2 chooses."
  - **Covered by CP2:**
    - K1-026 (Zarattini and Aziz, a 5-minute opening-range rule on QQQ): family B on the Nasdaq-100.
      Its stop and 10R target are excluded by the brief's rule 4 (X-06).
    - K1-013 (ICT liquidity sweeps on MNQ): family B, no evidential weight (X-08).
    - R-K1-079 (Pineda, the QQQ ORB retest): descriptive.
    - D.1 B4 and B8 (ORB on index futures).
  - **MNQ-specific prior already in the program:** D.1 B5 (Mesfin, arXiv 2605.04004, ORB on MNQ). The
    MES B-H1 module's pre-registration quotes it: HOLD_MINUTES = 5 "did NOT clear friction
    (T=-0.82)"; HOLD_MINUTES = 75 "cleared friction on the point estimate (T=0.88) for MNQ's lower
    cost structure" (Mesfin 2026, Table 4, as cited in that docstring).
  - **Counter-evidence:** R-K1-078 (Fetna 2026, "Opening-range breakout does not survive trading
    costs", a pre-registered study on nine futures including equity indices). Its abstract is
    reachable through Crossref, but no [K1] passage is logged.
- **MES record:** B-H1 hold 75 is class C2, which was null on MES (docs/NULL_CRITERIA.md; D.1f,
  commit ca8befb). Given the siblings' correlation with the S&P (the lead's note), these trials are
  close to the MES record.
- **Instantiated:**
  - **Opening range:** the bars opening in [08:30, 08:45).
  - **Eligible entry bars:** those opening in [08:45, 15:00). No entry from 15:00 CT on.
  - **Buffer:** 4 ticks of the exposure's most active contract (D1 table). Micro and mini share
    the tick in points, so the buffer does not depend on the vehicle.

    | Exposure | Most active contract (D1) | Buffer | Per contract (micro / mini) |
    |---|---|---|---|
    | Nasdaq-100 | MNQ, tick 0.25 | 1.00 index point | $2.00 MNQ / $20.00 NQ |
    | Russell 2000 | RTY, tick 0.10 | 0.40 index point | $2.00 M2K / $20.00 RTY |
    | Dow | MYM, tick 1.0 | 4 index points | $2.00 MYM / $20.00 YM |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is
    <= OR_low - buffer sells. The comparisons are non-strict, as in the MES module. One entry per
    trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it: the exit intent is
    emitted on the 75th bar after the entry-intent bar and fills at the next open. The engine's
    flatten at F applies to entries filled after 13:53, so the shortest possible hold is 8 minutes
    (a fill at 15:00 flattened at 15:08).
  - **Holding horizon:** 75 minutes, shorter only when F binds. **Session window:** 08:46 to 15:08
    at the latest.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is
  known at 08:45 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks of the most active contract, hold 75 minutes (D6, a
  literal port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes (at least 8). Floor ok; the
  10-minute mean is checked at screening.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: yes, by the forced flatten at the latest.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. Star rules: CPI window not touched (the earliest fill is 08:46); mini-halt note.
  5. News: <= 1 lot-equivalent. A position may be open at the 13:00 FOMC statement, which F6.3
     allows below full maximum size.
  6. Event-minute guard: an entry or exit fill landing in [13:00, 13:02) on an FOMC day fills at
     13:02. Dow fills in [09:00, 09:02) on ISM Services days do the same (C10).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows.
- **Trials in N:** 3.

### K1-cp3-01 (core port CP3, prior-close location)
- **Cluster** K1. **Products read:** own vehicle.
- **Exposures:** Nasdaq-100, Russell 2000, Dow, each traded only if D2 admits it. **Vehicle:** D2
  (chosen in E.2).
- **Session constants:** O = 08:30, C = 15:00, F = 15:08 CT.
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L
    over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as
    Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells,
    market intent on the O bar of day d. Exit: first bar at or after C-2 min."
  - **Same clock as MES H6.** The equity row gives exactly the H6 module's constants (08:30 open,
    [08:30, 15:00) range, 14:59 close, 14:58 exit), so this port is H6 verbatim on the sibling
    indices.
  - **K1 log:** no passed item is H6. K1-002 (daily MACD) is a family H construction but not H6.
    D6 ports H6 only, so K1-002 is not covered (X-13).
- **MES record:** H6 is class C7, which was null on MES (docs/NULL_CRITERIA.md; D.1f, commit ca8befb).
  Given the siblings' correlation with the S&P (the lead's note), these trials are close to the MES
  record.
- **Instantiated:**
  - **Daily bar:** O_d = open of the 08:30 bar. H and L are taken over the bars opening in
    [08:30, 15:00). C_d = close of the 14:59 bar.
  - **Complete day** (Family H): the 08:30 and 14:59 bars exist, the date is not an early halt, and
    every bar in [08:30, 15:00) carries one instrument_id.
  - **Instrument guard:** d-1's bar carries the instrument_id of day d's 08:30 bar.
  - **CLV:** computed in ticks, with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells
    (non-strict, as H6).
  - **Entry:** market intent on the 08:30 bar of d, filling at the 08:31 open.
  - **Exit:** market intent on the first bar at or after 14:58, filling at the 14:59 open.
  - **Holding horizon:** 388 minutes. **Session window:** 08:31-14:59.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's
  bar is complete at 15:00 CT on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 388 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: ok.
  4. Star rules: the CPI window is never touched (the entry is 08:31); mini-halt note.
  5. News: holds through the 13:00 FOMC statement and the 09:00 ISM release at <= 1 lot-equivalent,
     below the full maximum (D9.5).
  6. Event-minute guard: no fill lands in a release minute (08:31 and 14:59).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows.
- **Trials in N:** 3.

### K1-vxnband-01 (Nasdaq-100: fade a breach of the VXN/16 band, only at VXN extremes)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source (Seeck) covers 2018-2026 with an out-of-sample 2023-2026, overlapping both the confirmation and the research windows (docs/NULL_CRITERIA_E.md section 3).]
- **Cluster** K1. **Products read:** the Nasdaq-100 vehicle's bars and the VXN daily close (C9).
- **Traded exposure:** Nasdaq-100 {MNQ, NQ} only; the source tests NQ. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:** when NQ moves beyond a band of plus or minus one implied daily standard deviation
  (VXN/16) around the prior close, the move tends to revert before the session closes. A fade with
  a 30-minute exit earns only when VXN is at an extreme.
  - K1-005 (Seeck 2026, abstract only), P-K1-005-a: "The band is set daily as ± VXN/16 relative to
    the prior-session close; dividing by 16 converts the annualised VXN to a one-day
    standard-deviation estimate."
  - P-K1-005-b: "the 30-minute exit rule generates positive Sharpe only at the extremes (VXN < 20:
    0.38; VXN >= 30: 0.64), with slightly negative values in between. Walk-forward validation
    confirms the pattern out of sample (IS 2018–2022, n = 298, Sharpe = 0.47; OOS 2023–2026, n =
    191, Sharpe = 1.29)."
  - **Support for the band scale:** K1-006 P-K1-006-a. Using prior-day VIX, "The estimated slope is
    1.001" for the Nasdaq-100's maximum one-sided excursion from the open on VIX/√252. An
    implied-volatility index divided by about 16 therefore sizes the Nasdaq-100's typical daily
    excursion.
  - **Support for the high-VXN side:** K1-025 P-K1-025-b, "very high levels of implied volatility
    can on a statistical basis be viewed as signalling an imminent increase in stock indices, at
    least on a short term basis". This fits fading downside breaches when VXN >= 30 [inference].
  - **New to the program.** The log tags this as a port of D.1 families C and D with a new element:
    the band and the regime come from an external implied-volatility index. It is not an MES re-run:
    - MES C-H1 fades only small-to-moderate moves: "Large moves are deliberately NOT faded"
      (C-H1 module docstring).
    - MES D-H1 gates on trailing realized volatility.
    - MES D-H4 fades the overnight gap at the open.
    - This member reads an implied-volatility index, fades moves beyond one implied daily standard
      deviation at any RTH minute, and trades only at the index's extremes.
- **Conflicting evidence and quality:**
  - Abstract only (SSRN returned 403); single author.
  - The Sharpe ratio is non-monotone across the VXN buckets ("slightly negative values in between",
    P-K1-005-b).
  - "A pre-sample from 2010–2017 gives a Sharpe of -0.94 without the regime filter" (P-K1-005-b).
  - The 85.2% "reversion rate" (P-K1-005-a) is a touch-back rate, not a P&L.
  - The bucket edges 20 and 30 and the IS/OOS split are the author's own choices.
- **Definitions (day d):**
  - C_prev = close of the vehicle's 14:59 bar on the previous complete trade date (Family H
    completeness). Instrument guard: that bar carries the instrument_id of d's 08:30 bar; otherwise
    no trade on d.
  - V = the Cboe VXN close for the calendar date of trade date d-1. If it is missing, no trade on d.
  - w = C_prev x V / 1600. The band is U = C_prev + w and L = C_prev - w.
- **Regime condition:** trade on d only if V < 20 or V >= 30.
- **Entry rule:** on the first bar opening in [08:30, 14:29) whose close is > U, SELL q_c; whose
  close is < L, BUY q_c (market intent, filling at the next open). At most one entry per trade date:
  the first breach on either side.
- **Exit rule:** market intent on the 30th bar after the entry-intent bar, filling 30 minutes after
  the entry fill. The latest entry-intent bar is 14:28, which fills at 14:29 and exits at 14:59.
- **Holding horizon:** 30 minutes. **Session window:** 08:31-14:59 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close and instrument_id (C8; paid; history 2019-05..2026-06). C_prev is
    available at 15:00 CT on d-1.
  - VXN daily close: Cboe's public file (C9; free; E.2 confirms coverage 2019-04-30..2026-06-18).
    It is used from 08:30 CT on d.
- **Order type:** market. **Sizing:** q_c.
- **Parameters (every value):**
  - 16 (P-K1-005-a). 1600 = 100 x 16, because VXN is quoted in percentage points (P-K1-005-a).
  - VXN cuts 20 (strict) and 30 (non-strict), exactly as P-K1-005-b writes them.
  - Hold 30 minutes (P-K1-005-b).
  - Entry-intent bars opening in [08:30, 14:29). Judgment: every hold then ends by the 14:59 fill,
    before the settlement minute.
  - C_prev = the 14:59 bar close. Judgment: the abstract does not define "prior-session close"
    further. The RTH close is the program's daily-bar close (CP3's C_d) and the futures close
    nearest in time to VXN's own daily close.
  - RTH bars only (judgment, for the same reason).
  - Strict breach inequalities (judgment: "beyond" the band).
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date, held 30 minutes.
  - P-K1-005-b's counts (298 events in 2018-2022 and 191 in 2023-2026) imply roughly 0.2-0.25
    entries per trade date, if the counts are the extreme-bucket events [inference]. If they
    include every bucket, the member trades less.
  - Floor ok: 1 entry a day at most, holds of 30 minutes.
- **Falsification:**
  - The standard condition.
  - Member-specific (descriptive, not a separate trial): report the confirmation-window mean net P&L
    separately for V < 20 days and V >= 30 days. The source claims both extremes are positive
    (P-K1-005-b), so a negative mean in either regime counts against the mechanism as sourced.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: one trade a day, no stops. A breach can occur at the 08:30 bar after a gap. The fill is
     still the engine's next-open fill with modelled slippage, not a stray fill, so this is not the
     "reckless trades in gapped markets" pattern [judgment].
  4. Star rules: MNQ is starred. The CPI window is never touched (the earliest fill is 08:31).
     Mini-halt note if D2 picks NQ.
  5. News: <= 1 lot-equivalent.
  6. Event-minute guard: an entry or exit fill landing in [13:00, 13:02) on an FOMC day fills at
     13:02. D8 charges the event-window cost on fills in [13:00, 13:30).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11. On V >= 30 days the 2% proximity rule and Topstep's temporary mini halts
     are the most likely to bind. Both skip or cut trades and are part of the member as deployed.
- **Data needed:**
  - Nasdaq-100 vehicle ohlcv-1m over the research and confirmation windows.
  - VXN daily closes for every trade date before a research or confirmation date (Cboe, free).
- **Trials in N:** 1.

### K1-vwap-01 (Nasdaq-100: stop-and-reverse around the session VWAP, rewritten to D9's floor)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source sample is 2018-01 to 2023-09, overlapping the confirmation window.]
- **Cluster** K1. **Products read:** the Nasdaq-100 vehicle's bars only.
- **Traded exposure:** Nasdaq-100 {MNQ, NQ}; the source trades QQQ and TQQQ on the same index.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** hold long while price is above the session VWAP and short while it is below, and
  hold nothing overnight.
  - K1-027 (Zarattini and Aziz 2023, full text), P-K1-027-a: "The portfolio maintains a long
    exposure when QQQ is trading above the VWAP and reverses its exposure when the price of QQQ
    moves below the VWAP. No positions are held overnight."
  - P-K1-027-d: "a maximum drawdown of just 9.4% and a Sharpe Ratio of 2.1", on 1-minute QQQ data,
    2018-01-02..2023-09-28.
  - **New to the program.** No MES member uses VWAP. The log tags this as a port of D.1 families B
    and F. D.1 C24 (a Databento note on VWAP-to-mid deviations, not carried) is the only VWAP row
    in D.1's log.
- **Conflicting evidence and quality:**
  - "we assumed no slippage in our order fills" (P-K1-027-b).
  - Trade count: "The active VWAP strategies incurred about 22,000 trades" (P-K1-027-c). Over about
    1,440 trade dates (1,498 weekdays less holidays) that is about 15 a day [arithmetic].
  - The hit ratio is "approximately 17%" (log, Sec. 3.7).
  - At Topstep's $1.22 MNQ round turn, commissions alone come to about 15 x $1.22 = $18.30 per
    contract per day before slippage [arithmetic]. The result is cost-fragile.
  - No out-of-sample test; practitioner authors.
  - D6 criterion 2 records that MES's high-frequency trials (C3 and C6) were its most negative
    members.
- **D9 rewrite.** The source's rule can breach D9.3(a) (no daily cap) and D9.3(b) (1-minute flips),
  so the minimum hold and the entry cap below are added. This is a declared change to the source's
  rule.
- **Definitions (on the vehicle's bars, trade date d):**
  - Typical price TP_b = (high_b + low_b + close_b) / 3.
  - VWAP_t = sum(TP_b x volume_b) / sum(volume_b) over the bars b opening from 08:30 through bar t
    inclusive. It is known at the close of bar t.
  - s_t = +1 if close_t > VWAP_t; -1 if close_t < VWAP_t; otherwise s_{t-1} (0 before the first
    sign of the day). If sum(volume) = 0, no action is taken on that bar.
- **Entry and exit rule**, evaluated on every bar t opening in [08:30, 14:57):
  - If flat, s_t is non-zero and fewer than 20 entries have been made today: a market intent in
    direction s_t.
  - If the position is opposite to s_t and its minimum hold is met: a market intent to exit. If
    fewer than 20 entries have been made today, it is accompanied by a second market intent in
    direction s_t. Both fill at the next open.
  - Otherwise nothing.
  - **Minimum hold (D9.3(b)):** a position filled at the open of bar k may be exited only by an
    intent on bar k+1 or later. It therefore fills at the open of bar k+2 or later, at least 2 full
    minutes after entry.
  - **Entry cap (D9.3(a)):** entries are counted per trade date, including the new leg of each
    reversal, with at most 20. After the 20th, the next opposite signal (once the minimum hold is
    met) exits to flat for the rest of the day.
  - **Final exit:** a market intent on the first bar at or after 14:58, filling at the 14:59 open.
    No entry intent is sent from the 14:57 bar on; the latest entry fills at 14:57 and exits at
    14:59.
- **Holding horizon:** variable, from 2 to 388 minutes. The source's rate implies a mean near 25
  minutes (a 390-minute session over about 15 positions) [inference]. **Session window:**
  08:31-14:59 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m high, low, close, volume and instrument_id (C8; paid). If
  E.2 declares the full-size contract's bars as the price path, that contract's volume enters VWAP
  (same underlying). A change of instrument_id within the day: no new entry after it, and the
  position is closed on the next bar.
- **Order type:** market only. A reversal is two market intents, never a stop order. **Sizing:**
  q_c.
- **Parameters (every value):**
  - RTH start 08:30 and flat before the close: P-K1-027-a ("No positions are held overnight";
    QQQ's session is 08:30-15:00 CT).
  - Exit at 14:58 = C-2. Judgment: the program's daily exit convention, as in CP1 and CP3.
  - TP-based VWAP. Judgment: the standard ohlcv-1m approximation; the source's exact computation is
    [unverified].
  - A tie keeps the previous sign (judgment).
  - 20 entries and the 2-minute hold (D9.3).
  - **Grid:** none.
- **Expected entries and hold:** about 15 entries a day (the source's rate), capped at 20. The floor
  holds by construction for (a) and (b); (c) is checked at screening.
- **Falsification:**
  - The standard condition.
  - Member-specific (descriptive): report the confirmation-window mean entries per day and the mean
    gross (pre-cost) P&L per contract per day beside the net figure. If gross is positive and net
    is not, the cost-fragile reading of the source is confirmed.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: at most 20 entries a day, each held at least 2 minutes, far from "hundreds of rapid
     trades". It is not built to exploit SIM fills: the harness charges slippage on every fill.
  4. Star rules: MNQ is starred. The CPI window is never touched (the earliest fill is 08:31).
     Mini-halt note.
  5. News: <= 1 lot-equivalent; the position never exceeds q_c.
  6. Event-minute guard: fills in [13:00, 13:02) on FOMC days are moved to 13:02, which can delay a
     reversal. D8 charges the event-window cost on fills in [13:00, 13:30).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent. A reversal's two intents net to q_c.
  9. Price limit: C11.
- **Data needed:** Nasdaq-100 vehicle ohlcv-1m, with volume, over the research and confirmation
  windows.
- **Trials in N:** 1.

### K1-predrift-01 (Dow: follow the pre-release move into the ISM Services release)

> [EXCLUDED by the lead, 02:15 PDT 2026-09-24, answering this writer's question 2: this is MES's scheduled-macro-drift family (E-H1/E-H2, class C5, null on MES under docs/NULL_CRITERIA.md) re-run on the Dow, a sibling index highly correlated with the S&P; the K1 brief allows MES families only through the core ports. K2-predrift-01 (the rates version) is unaffected. 0 trials. The entry is kept below for the record only.]
- **Cluster** K1. **Products read:** the Dow vehicle's bars and the ISM release calendar (C9).
- **Traded exposure:** Dow {MYM, YM}. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Prices drift in the direction of the news before scheduled US releases, and this
  catalog's trade rule follows that drift through the release.
  - K2-007 (Kurov, Sancetta, Strasser, Wolfe 2019, JFQA; full text; panel source claimed by K2),
    P-K2-007-a [K1][K2]: "Prices begin to move in the 'correct' direction about 30 minutes before
    the release time. The pre-announcement price drift accounts on average for about 40% of the
    total price adjustment."
  - It is shown on E-mini S&P 500 futures, with the E-mini Dow among the robustness markets:
    "markets (E-mini Dow stock index and 30-year Treasury bond futures). All tests confirm
    robustness of our [results]." (P-K2-007-f).
  - ISM Non-Manufacturing is one of the drift announcements: "the S&P 500 futures prices increase
    on average by 0.104 percent before a one standard deviation positive surprise in the ISM
    Non-Manufacturing Index" (P-K2-007-c). Table 2 gives "0.104 (0.017)***" (P-K2-007-d).
  - Against costs: "The median effective bid-ask spread is 0.020% for the E-mini S&P 500 futures
    ... far below the two standard deviation band of the CAR around drift announcements"
    (P-K2-007-e).
  - **Reasoning (the trade rule is this catalog's, not the paper's):** if the pre-release move
    carries about 40% of the adjustment in the direction of the news, its sign predicts the sign of
    the remaining adjustment, which arrives at the release. A position taken in the drift's
    direction one minute before the release, and held through it, collects that remainder.
  - **New to the program, not an MES re-run.** This paper is D.1 log row E19 ("Price drift before
    U.S. macroeconomic news: private information?", ECB WP 1901), which was not retrieved or carried
    and was never an MES member. MES E-H1 goes long before FOMC, CPI and NFP releases whatever the
    direction; E-H2 trades post-release momentum after a range expansion (module docstrings).
    Neither signs a position by the pre-release move.
- **Conflicting and weakening evidence:**
  - The paper's primary product is the S&P. The Dow evidence is one robustness sentence
    (P-K2-007-f).
  - The [K1] passages name only ISM Non-Manufacturing among the "Nine of the 20 announcements"
    (P-K2-007-a), so only that release is used.
  - The sample is 2008-2014 (K2 log).
  - The drift per one standard deviation of surprise (0.104%) is smaller than "one standard deviation
    of 5-minute returns ... for the stock ... markets is 0.12" percent (P-K2-007-c). So the sign of a
    single pre-release move is a noisy predictor [inference].
  - K2-015 P-K2-015-a [K1] ("news produces conditional mean jumps") implies no drift after the
    release, which is why the exit comes soon after it.
- **Event days:** trade dates carrying ISM's Services (formerly Non-Manufacturing) PMI release,
  "released on the third business day of the month at 10:00 a.m. (EST)" (both captures). The
  release time is T = 09:00 CT.
  - A date counts only if it appears in the ISM table for its year as captured before that date.
    E.2 builds the tables from the captures (C9) and cross-checks them against ISM's actual
    publication record.
  - Dates the table moves use the table's date, for example "**Services PMI moved due to 4th of July
    holiday observed on July 3, 2026".
- **Entry rule:**
  - D = close of the bar at 08:58 minus close of the bar at 08:29, the move from 08:30 to 08:59
    (T-30 to T-1).
  - D > 0: BUY q_c. D < 0: SELL q_c. D = 0: no trade.
  - Market intent on the 08:58 bar, filling at the 08:59 open, one minute before T.
  - Both bars must exist with one instrument_id.
- **Exit rule:** market intent on the 09:09 bar, filling at the 09:10 open (T + 10).
- **Holding horizon:** 11 minutes. **Session window:** 08:59-09:10 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close and instrument_id (C8; paid).
  - The ISM calendar: free through Wayback, 2020-08..2026-08. The 2019-05..2020-07 tables are for
    E.2 to source. Each year's table is published ahead of time (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters (every value):**
  - T = 09:00 CT (ISM calendar).
  - The 30-minute signal window (P-K2-007-a, "about 30 minutes before the release time").
  - Entry at T-1. Judgment: the last bar-open fill before the release, which also lets the signal
    cover 29 of the 30 minutes.
  - Exit at T+10. Judgment: the paper's total-impact window ends 5 minutes after the release (K2
    log, products-and-horizon line), but an exit at T+5 would hold 6 minutes and break D9.3(c)'s
    10-minute mean. T+10 is the first whole-minute exit that meets it with a margin. The extra 5
    minutes are undocumented and, per P-K2-015-a, expected to carry no drift.
  - **Grid:** none.
- **Expected entries and hold:**
  - 12 releases a year: about 15 on research-window dates (April 2025-June 2026) and about 57 on
    confirmation dates (June 2019-February 2024; May 2019's third business day falls before the
    earliest S_X), before exclusions [calendar arithmetic].
  - At most 1 entry per event day, held 11 minutes. Floor ok.
- **Falsification:**
  - The standard condition. With about 57 confirmation events, the D4 power check may label it
    "inconclusive by design" (section 7).
  - Member-specific (descriptive): report the hit rate of sign(D) against the sign of the move from
    the 08:59 open to the 09:10 open.
- **Topstep check:**
  1. Flat by F: last fill 09:10.
  2. Order type: market.
  3. D9.4: one trade per event day. The entry fills before the release at the engine's next-open
     fill, not in a gapped market.
  4. Star rules: MYM is starred. The CPI window (07:25-07:35) is never touched. Mini-halt note if D2
     picks YM.
  5. News: the member holds at most 1 lot-equivalent through a scheduled release. F6.1 allows that,
     and F6.3's prohibition covers only "full Maximum Position Size".
  6. Event-minute guard: no fill in [09:00, 09:02); the fills are at 08:59 and 09:10. The D8
     event-window cost applies to the 09:10 exit (C10).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:**
  - Dow vehicle ohlcv-1m over the research and confirmation windows (the rule reads only 08:29-09:10
    on event dates).
  - The ISM Services release calendar, 2019-2026.
- **Trials in N:** 1.

### K1-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 table, 2026 Jan-Aug ADV): Nasdaq-100, then Russell 2000, then Dow; if none is admitted, no ML member. The features are unchanged (they read their named products as signals).]
- **Traded vehicle: Nasdaq-100 exposure** {MNQ, NQ}; D2 chooses the contract in E.2.
  - **Reason:** most of the log's intraday evidence is on the Nasdaq-100:
    - K1-001, 005, 006, 007, 009, 010, 013, 014, 015, 025, 026 and 027 (12 items; K1-012 covers
      all four pairs);
    - the Dow has K1-008, K2-007's robustness sentence and the daily K1-002;
    - the Russell 2000 has only reconstitution descriptions (K1-017, 018, 019, 022, 023) and a
      spread construction (K1-021), none directional.
  - MNQ also has the cluster's highest ADV, 2,363,465 (D1 table).
  - **No fallback is declared.** KF1 and KF2 are Nasdaq-100-specific (VXN). If D2 admits no
    Nasdaq-100 contract, the lead decides.
- **Products the features read:**
  - the Nasdaq-100 vehicle (v; tick 0.25);
  - MES ohlcv-1m bars (the S&P leg; owned; research-window and confirmation-window dates only, never
    holdout);
  - the Russell 2000 exposure's vehicle bars, or its declared price path (r);
  - VXN daily closes (C9).
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12. Throughout, t_j is the
  decision time, and "the bar at t_j - 1" is the last bar closed at t_j. Every constant is a
  literal written here.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | vxn_prev | V_prev = Cboe VXN close for the calendar date of trade date d-1. Missing: no trade on d | K1-005 P-K1-005-b (the VXN buckets); K1-025 P-K1-025-a, P-K1-025-b (the implied-volatility level as a leading indicator) | published after d-1's session; used from 08:35 CT on d |
| KF2 | band_pos | (close of v's bar at t_j - 1 - C_prev) / (C_prev x V_prev / 1600). C_prev is the close of v's 14:59 bar on the previous complete trade date, whose instrument_id must equal that of d's 08:30 bar; otherwise no trade on d | K1-005 P-K1-005-a; K1-006 P-K1-006-a, P-K1-006-b | t_j |
| KF3 | nq_es_rel | 10000 x [close_v(t_j - 1) / open_v(08:30) - close_MES(t_j - 1) / open_MES(08:30)], in basis points. If any of the four bars is missing, or either leg changes instrument_id within [08:30, t_j): no trade at t_j | K1-020 P-K1-020-a, P-K1-020-b (the Nasdaq against S&P relative-value construction) | t_j (MES bars closed <= t_j) |
| KF4 | rty_es_rel | 10000 x [close_r(t_j - 1) / open_r(08:30) - close_MES(t_j - 1) / open_MES(08:30)], same missing-bar rule | K1-021 P-K1-021-a (the small against large cap construction) | t_j |
| KF5 | vwap_dev | (close_v(t_j - 1) - VWAP_v) / 0.25, where VWAP_v = sum(TP x volume) / sum(volume) over v's bars opening in [08:30, t_j) and TP = (high + low + close) / 3. If sum(volume) = 0: no trade at t_j | K1-027 P-K1-027-a | t_j |
| KF6 | or5 | (close of v's 08:34 bar - open of v's 08:30 bar) / 0.25 | K1-026 P-K1-026-b (the first 5-minute candle's direction) | 08:35 CT |
| KF7 | vol_open_ratio | volume of v's 08:30 bar / the mean volume of v's 08:30 bar over the 20 most recent earlier complete trade dates (all 20 required; otherwise no trade on d) | K1-014: the classifier's "first-bar volume well above baseline" component (log mechanism line) and P-K1-014-a | 08:31 CT; earlier dates only |

- **Decision window [W0, W1] = [08:35, 14:05] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 08:35, 09:05, ..., 14:05, 12 a day. W1 + h = 14:35 <= F.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 to the open of t_j + 30.
    Entry fills therefore fall at :06 or :36, and exit fills at :05 or :35.
  - **Why W0 = 08:35:** the first five-minute candle (P-K1-026-b), and so KF6, is complete at 08:35.
    The :05/:35 grid keeps every fill out of the 09:00 CT ISM release minutes and the 13:00 CT FOMC
    minutes (D9.5a), and out of the 07:25-07:35 CPI window.
  - **Why W1 = 14:05:** the last position ends at the 14:35 open. That is before the 14:50-15:00
    closing-auction period, which the log flags as behaving differently in the futures
    (P-K1-011-a, P-K1-011-b; P-K1-024-b) and which no member here models, and before the 15:00
    settlement minute.
  - **Why h = 30:**
    - The log's only tested intraday exit horizon on NQ is K1-005's "30-minute exit rule"
      (P-K1-005-b).
    - K1-003's holds of 5 ms to 5 minutes lose after the spread (P-K1-003-c), which argues against
      15.
    - K1-009's null target runs from the 10:30 ET bar to the close (P-K1-009-a). As a prior
      [judgment], that argues against the long horizons (60, 120).
- **Expected rows:** 12 x the eligible research-window trade dates. That is about 305 trade dates,
  less about 15 roll-blackout dates, early-halt and vendor-degraded dates, and the 20-date warm-up of
  B4 and KF7: roughly 3,000-3,400 rows. E.2 gives the exact count.
- **Expected entries:** at most 12 a day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of the mean net daily P&L per contract below eps
  at >= 80% achieved null power on the confirmation window counts against it). Failing the D5
  screen puts it in Tier B. Prior: K1-009, an ML study on MNQ, found "No configuration produces
  out-of-sample accuracy materially above base rate" (P-K1-009-a).
- **Topstep check:**
  1. Flat by F: last exit 14:35.
  2. Order type: market (D15.6).
  3. D9.4: at most 12 entries a day, 30-minute holds, no stops or brackets.
  4. Star rules: MNQ is starred. The CPI window is not touched. Mini-halt note if D2 picks NQ.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span the 09:00 ISM and
     13:00 FOMC releases.
  6. Event-minute guard: no fill in [09:00, 09:02) or [13:00, 13:02). D8 charges the event-window
     cost on the 13:05 exit and 13:06 entry fills on FOMC days, and on the 09:05 and 09:06 fills
     on ISM days if the lead extends ISM to the Nasdaq-100 (C10).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:**
  - ohlcv-1m of v and r over the research window (training and tuning) and the confirmation window
    (the frozen model).
  - MES bars on those two windows only (owned).
  - VXN daily closes.
  - Member-level coverage checks for v, r and MES over 08:30-14:35.
  - If D2 does not admit the Russell 2000, E.2 must still buy r's history for KF4, or the lead drops
    KF4 before any fit.
- **Trials in N:** 1 at confirmation. In the research-window accounting the grid counts as 48
  (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K1-vixfut-01 | Trade NQ or ES on VIX-futures moves (K1-003) | D9.3 floor; evidence; data | The lead exists only at 5 ms to 5 minutes and loses after the spread: "this strategy generates negative returns irrespective of the holding period" (P-K1-003-c). VX is a CFE contract, not in GLBX.MDP3. The traded product in the paper is ES, which is closed. Non-survivor |
| X-02 K1-microlead-01 | Micro against E-mini lead-lag within one exposure (K1-012, K1-001, K1-015, K1-016) | D9.3 floor; evidence; data | Price leadership is measured "up to one second" (P-K1-001-b), and the micros "contribute approximately equal amounts" (P-K1-012-a), which is evidence against a tradable gap. K1-015 and K1-016 need trader-type codes (P-K1-015-a, P-K1-016-a) and a floor contract that no longer trades |
| X-03 K1-ndxrecon-01 | NQ on the Nasdaq-100 rebalancing date (last 30 minutes) and the next morning (K1-004) | Rule 1 (no index-level sign) | The effect is stock-level: promotions and demotions move in opposite directions, "especially during the last 30 minutes" and reversing "during the early trading hours on the day following" (P-K1-004-b). The net index-level sign is not measured, so no direction can be traced. Abstract only; working paper |
| X-04 K1-rtyrecon-01 | RTY or M2K on the Russell reconstitution day (K1-017, 018, 019, 022, 023) | Rule 1 (no directional claim); frequency | The CME pages describe volume, "one of the highest trading volume days of the year" (P-K1-017-a), and index-tracker trades "on the cash close" (P-K1-022-a), with no claim about RTY's price path. The flow sits at 15:00 CT, C itself. There are one or two events a year. The 2026 schedule is in conflict (November, P-K1-018-b, against December, P-K1-023-a; fetch 6 did not resolve it) |
| X-05 K1-closeauct-01 | Short NQ, RTY or YM over the closing-auction window [14:50, 15:00) (K1-011; K1-024) | Rule 1; D9.3(c); data | The only futures-side evidence is TAIFEX, abstract only, with a garbled direction claim ("will increase their price and lowers their average return", P-K1-011-b) and a hidden auction unlike the published US imbalances (log). The documented window is 5 minutes, which fails the 10-minute mean hold unless stretched to an undocumented 10. NYSE imbalance data is paid and not in the plan, with an unconfirmed history start; Nasdaq's closing-cross data is not covered (P-K1-024-a). The lead may admit a 3-trial version (market intent on the 14:49 bar, exit intent on the 14:59 bar, short, on each exposure); it is not written here |
| X-06 K1-orb5-01 | The first 5-minute candle's direction on the Nasdaq-100, entered at 08:35 (K1-026) | Rule 4 (stops and targets); covered by CP2 | The sourced rule depends on "The stop loss was placed at the low of the day ... We set the profit target at 10x the $R" (P-K1-026-b). Both are prohibited. A stop-free version is an untested construction. Its family (opening range on the Nasdaq-100) is **covered by CP2**. Counter-evidence: no slippage (P-K1-026-b), stop parameters tuned in-sample (log), D.1 B5 on MNQ, R-K1-078 |
| X-07 K1-ictamd-01 | ICT "accumulation-manipulation-distribution" on NQ (K1-007) | Non-survivor | "no directional information beyond the daily trend regime was observed" (P-K1-007-b); "57% of valid signals see full target delivery before the 9:40 AM New York entry window opens" (P-K1-007-a) |
| X-08 K1-ictconf-01 | ICT confluence entries on MNQ (K1-013) | Rule 1 | A one-page high-school abstract with no sample, costs or test ("11% increase in win rate compared to manually trading", P-K1-013-b). The confluences are discretionary and unspecified. Family B, covered by CP2 |
| X-09 K1-dowopen-01 | YM short-side opening reversal (K1-008) | Rule 1 (parameters) | "Exact trading parameters are withheld, limiting independent replication" (P-K1-008-b), so no trigger can be traced. The source's own pre-2023 sample is "below breakeven" at 45.22% (P-K1-008-b), and the confirmation window 2019-05..2024-02 is mostly pre-2023. The expectancy is gross only |
| X-10 K1-stress-01 | Trade MNQ's late-session reversal on "high-stress" classifier days (K1-014) | Non-survivor | "Eight directional strategy configurations were tested on classifier-positive days. None passed" (P-K1-014-b). It rests on 40 event days, and "2024 produced a net loss". The first-bar volume component enters K1-ml-01 as KF7 |
| X-11 K1-mnqml-ext | Another hand-built ML forecast of the MNQ close (K1-009) | Non-survivor; D15 | "No configuration produces out-of-sample accuracy materially above base rate" (P-K1-009-a); the permutation p-value is 0.135 (P-K1-009-d). The cluster's one ML trial is K1-ml-01 (D15), which cites this as its prior |
| X-12 K1-hurst-01 | Hurst-regime filter on NQ 5-minute bars (K1-010) | Rule 1 (unspecified base rule) | The base entry rule is not in the abstract. The validation is Monte Carlo, not out-of-sample (P-K1-010-b). The P&L is quoted per trade in dollars without a contract count (P-K1-010-a) |
| X-13 K1-macd-01 | MACD crossover on YM and NQ (K1-002) | Flat by F; D6 | "a buy (or sell) order ... is executed at the closing price ... on the next day ... a reverse trade is automatically executed" (P-K1-002-b) means holding across days. An intraday-hold variant would be an untested family H construction, and D6 ports H6 only. Also "Transaction fees are not taken into account" (P-K1-002-c) and "no 'P-P' model that consistently generated significant returns" (P-K1-002-d). The Nikkei leg is out (D1) |
| X-14 K1-vxnlong-01 | Long NQ intraday when VXN is "extremely high" (K1-025) | Rule 1 (threshold, horizon) | P-K1-025-b gives no threshold and an unverified horizon ("at least on a short term basis"; the log thinks it is multi-day). The sample predates 2003. An intraday hold would test an undocumented horizon. Used only as support: K1-vxnband-01 and K1-ml-01 KF1 |
| X-15 K1-vixrange-01 | Trade the VIX/√252 expected-move band on the Nasdaq-100 (K1-006) | Rule 1 (no P&L, no direction) | It is a range calibration: "touched intraday in 37.5% of sessions" (P-K1-006-a). The 54.8% lower-first touch (P-K1-006-b) has no cost or P&L test. Used as support for K1-vxnband-01 and KF2 |
| X-16 K1-spread-01 | NQ-ES or RTY-ES intraday relative value (K1-020, K1-021) | Rule 1; D1.5 | These are definitions, not evidence: "The point of entering into an inter-market spread is to trade on the differences" (P-K1-020-b); "two E-mini Russell 2000 futures for every one E-mini S&P 500" (P-K1-021-b, illustrative). The ES leg cannot be traded (D1.5). An NQ-RTY spread has no logged source. Used as KF3 and KF4 |
| X-17 K1-chpmi-01 | NQ or YM on the Chinese PMI release (K3-007 [K1], P-K3-007-h, P-K3-007-i: "E-mini Nasdaq-100 35 0.10 (0.03)*** 0.463; E-mini Dow 35 0.09 (0.02)*** 0.467") | Rule 3 (consensus); contemporaneous | The effect is a surprise response against a consensus that is proprietary. It is measured in a [-10, +10] minute window ("from 10 minutes before to 10 minutes after", P-K3-007-c [K3]) and "appears to be permanent" (K3 log, first-run passage, not re-checked), so nothing is left to trade afterwards. N = 35 |
| X-18 K1-macrojump-01 | Post-release trade on US macro surprises (K2-015 [K1], P-K2-015-a) | Rule 3; contemporaneous; product | "news produces conditional mean jumps" at the release, with state-dependent signs (K2 log). The K1 products in the paper are the S&P 500 and Euro Stoxx 50 futures (not traded). It needs consensus surveys |
| X-19 K1-polunc-01 | Condition a K1 release member on monetary-policy uncertainty (K3-035 [K1], P-K3-035-a: "the response to macroeconomic news weakens in the stock and crude oil markets") | Rule 1; partition rule 4 | It is a conditioning variable for surprise responses, and K1 has no surprise member (X-17, X-18). The uncertainty measure is rates-derived and unspecified [unverified], so it is routed to K8 (section 4) |
| X-20 K1-volheat-01 | Volatility-transmission state on ES (K3-030 [K1], P-K3-030-a) | Rule 1; product | Volatility only, with no return claim, on ES (closed). B4 in the ML member already carries volatility state |
| X-21 K1-oireversal-01 | Overnight-intraday reversal on K1 products (K3-040, registry-tagged K1) | Rule 1 | Title only; content [unverified]. It is opposite in sign to CP1's (a) form |

---

## 3. Beyond budget (lead decides)

None. The log supports 3 new members inside a budget of 11. These candidates were considered and
not written (none is a budget overflow):
- **K1-vxnband-01 on the Russell 2000 and the Dow**, using those indices' own Cboe volatility
  indices.
  - Why not: the evidence is on NQ with VXN only (K1-005). The Russell and Dow volatility indices'
    names, availability and history were not checked in E.0.
  - Cost: +2 trials.
- **An unfiltered VXN-band fade** (every VXN level).
  - Why not: the source reports "slightly negative values" in the middle buckets and a -0.94
    pre-sample Sharpe without the filter (P-K1-005-b).
  - Cost: +1 trial.
- **K1-vwap-01 on the Russell 2000 and the Dow.**
  - Why not: the evidence is QQQ and TQQQ only.
  - Cost: +2 trials.
- **K1-predrift-01 variants.**
  - Candidates: on NQ or RTY (untested there); with the MES pre-release move as the signal (the
    paper's primary product, a K1 leg); or on the other eight drift announcements (not named in the
    [K1] passages).
  - Cost: +1 to +3 trials.
- **The stop-free first-candle rule (X-06)** and **the closing-auction short (X-05)**: +1 and +3
  trials.

---

## 4. Routed to K8

| Source | Legs | One phrase | K8 disposition (K8 log) |
|---|---|---|---|
| Kurov, Olson, Wolfe (2024), J. Commodity Markets, "Have the causal effects between equities, oil prices, and monetary policy changed over time?" (K1 log section 4) | equity index (K1), crude (K4), rates (K2) | time-varying equity-oil causality | F01, rejected (R-K8-001: contemporaneous) |
| Zangelidis and Rezitis (2026), Resources Policy, HAR-VAR volatility topology (K1 log section 4) | NASDAQ (K1), copper (K5), dollar (K3), commodity indices | volatility spillover topology | F02, rejected (R-K8-002) |
| Kurov, Stan (2018), K3-035 [K1] | monetary-policy uncertainty (rates-derived) conditioning the equity response to US news | conditioning variable from rates | routed by this catalog (X-19); not yet in K8's log |
| Alquist, Ellwanger, Jin (2020), K4-008 = K8-001 | WPSR oil shock (K4) and the S&P via SPY (K1 leg), Treasuries (K2), FX (K3) | oil inventory news as a cross-asset instrument | read by K8 |
| Baur, Kuck (2020), K8-003 | S&P 500 5-minute return (K1 signal) and gold (K5 traded) | flight-to-safety lead into gold | read by K8 |
| Mourey et al. (2025), K8-004 | weekend crypto (K7) and Monday equity indices (K1) | weekend crypto as an equity-open signal | read by K8 |
| Phan, Sharma, Narayan (2016), K8-007 | crude (K4) and the US equity market (K1) | intraday volatility interaction | read by K8 |
| K8-006 (CAD and crude, S&P as a conditioning leg); K8-008 (US cash-equity open and ZN) | K1 as a conditioning or clock leg | cross-cluster | read by K8 |

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K1.md section 3, every `[K1]`-tagged
passage in the other logs, the registry lines tagged K1, the log's rejection rows as a group, and the
D.1 rows the K1 log cites.

| Item | Disposition |
|---|---|
| K1-001 Hasbrouck (2003) | Excluded, X-02 (one-second price discovery; the lagging instruments are an ETF and a defunct floor contract). Background only |
| K1-002 Kang (2023), MACD | Not intraday-feasible (holds across days, P-K1-002-b); excluded, X-13 |
| K1-003 Bangsgaard, Kokholm (2024) | Excluded, X-01 (non-survivor after costs; 5 ms to 5 minutes). Used as a reason against h = 15 in K1-ml-01 |
| K1-004 Franz (2019) | Excluded, X-03 (stock-level; no index-level sign; abstract only) |
| K1-005 Seeck (2026) | **Used: K1-vxnband-01** (P-a, P-b); K1-ml-01 KF1 and KF2, and the choice of h |
| K1-006 Backhaus (2026) | Supporting evidence for K1-vxnband-01's band scale and K1-ml-01 KF2 (P-a, P-b). As a member, excluded, X-15 |
| K1-007 Taylor (2026), ICT AMD | Excluded, X-07 (non-survivor) |
| K1-008 Ladia (2026) | Excluded, X-09 (parameters withheld; the pre-2023 null covers most of the confirmation window) |
| K1-009 Mesfin (2026), LSTM and GB on MNQ | Non-survivor, X-11. Cited as K1-ml-01's prior and in its h choice |
| K1-010 Ntingana (2026) | Insufficient evidence: the base rule is unspecified; X-12 |
| K1-011 Chen, Tai, Yang (2013) | Excluded, X-05 (insufficient evidence; D9.3(c)). Cited for K1-ml-01's W1 |
| K1-012 Fassas (2021) | Excluded, X-02 (evidence against a micro-mini gap; sub-second) |
| K1-013 Parekh, Heller (2026) | Excluded, X-08 (no evidential weight). Family B, **covered by CP2** |
| K1-014 Mesfin (2026b) | Non-survivor, X-10. Its first-bar volume component is used as K1-ml-01 KF7 |
| K1-015 Kurov, Lasser (2004) | Insufficient evidence: background only, needs trader-type codes; X-02 |
| K1-016 Kurov (2008) | Insufficient evidence: background only, needs trader-type codes; X-02 |
| K1-017 CME (2023), Russell reconstitution | Excluded, X-04 (no directional claim) |
| K1-018 CME (2025), Russell reconstitution | Excluded, X-04. The source of the "November" side of the 2026 conflict |
| K1-019 CME (2021), reconstitution results | No mechanism (the log says "empty on reading"). Not used |
| K1-020 CME course, intermarket spreads | Construction only; excluded as a member, X-16. **Used: K1-ml-01 KF3** |
| K1-021 CME course, RTY spreads | Construction only; excluded as a member, X-16. **Used: K1-ml-01 KF4** |
| K1-022 CME, managing a reconstitution | Excluded, X-04 |
| K1-023 CME (2026), 2026 Russell reconstitution | Excluded, X-04. The source of the "December" side of the 2026 conflict |
| K1-024 Databento (2025), NYSE imbalance feeds | Data availability only; excluded, X-05 (paid, not in the plan). Cited for K1-ml-01's W1 |
| K1-025 Giot (2003/2005) | Excluded as a member, X-14. Supports K1-vxnband-01 (the high-VXN side) and K1-ml-01 KF1 |
| K1-026 Zarattini, Aziz (2023), ORB | **Covered by CP2** (family B on the Nasdaq-100); its stop and target structure is excluded, X-06. **Used: K1-ml-01 KF6** and W0 |
| K1-027 Zarattini, Aziz (2023), VWAP | **Used: K1-vwap-01** (P-a to P-d); K1-ml-01 KF5 |
| K2-007 [K1] Kurov, Sancetta, Strasser, Wolfe (P-a, P-c, P-d, P-e, P-f) | **Used: K1-predrift-01** (P-a mechanism; P-c, P-d for the ISM release; P-e cost context; P-f for the E-mini Dow). The same paper is D.1 log E19 (not retrieved there) |
| K2-015 [K1] Andersen, Bollerslev, Diebold, Vega (P-a) | Excluded as a member, X-18 (contemporaneous jumps; S&P and Euro Stoxx). Used in K1-predrift-01's exit reasoning |
| K3-007 [K1] Baum, Kurov, Wolfe (P-h, P-i) | Excluded, X-17 (proprietary consensus; contemporaneous; N = 35) |
| K3-030 [K1] Martínez, Tse (P-a) | Insufficient evidence for K1: volatility only, ES (closed); X-20 |
| K3-035 [K1] Kurov, Stan (P-a) | Excluded, X-19; routed to K8 (section 4) |
| K3-040 (registry-tagged K1) Kosowski et al. | Insufficient evidence: title only; X-21. Noted as counter-evidence in CP1 |
| K4-008 = K8-001 (registry-tagged K1) Alquist, Ellwanger, Jin | Routed to K8 and read by K8. The K1 leg there is SPY (S&P), not a traded K1 product |
| K4-043 Fett, McPhail (ES leg; no `[K1]` passage) | Not used: ES stop-order facts are D.1 B2's (generic S&P) |
| K4-050 / R-K1-078 Fetna (2026) | Insufficient evidence (no [K1] passage logged). Noted as counter-evidence for CP2 |
| K8-003, K8-004, K8-006, K8-007, K8-008 (K1 legs) | K8's (section 4) |
| R-K1-067, R-K1-068, R-K1-069 | Rejected in the log; the mechanism is **covered by CP1** (D.1 A10 and A28 family) |
| R-K1-078, R-K1-079 | Rejected or pointed elsewhere in the log; family B, **covered by CP2** |
| R-K1-028, 088, 090, 092 | Sentiment or attention, shelved (brief rule 13). No member conditions on sentiment. VXN and VIX are option-implied volatility indices, not sentiment measures |
| R-K1-001 to R-K1-095 (all others) | Rejected at pre-filter or on reading; not used |
| D.1 rows cited by the K1 log: A10 (and A28) | Covered by CP1 |
| D.1 B4, B5 (with A14 and C5), B8 | Covered by CP2; B5 is quoted there as an MNQ prior |
| D.1 E10, E13, E14 (S&P rebalance and passive-flow pressure) | Generic S&P (D.1 territory); no K1 member. K1's own reconstitution items are X-03 and X-04 |
| D.1 C16 (end-of-day reversal, cross-sectional stocks) | Not a K1 product; not used |
| D.1 E19 (price drift before US news) | The same paper as K2-007; used through K2-007's [K1] passages in K1-predrift-01 |
| Registry note | The K1-001 claim line carries a wrong DOI, as the log says (correct: 10.1046/j.1540-6261.2003.00609.x). The registry is append-only, so it is not edited here |

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all three admitted) |
|---|---|---|---|
| K1-cp1-01 | Nasdaq-100, Russell 2000, Dow | 1 | 3 |
| K1-cp2-01 | Nasdaq-100, Russell 2000, Dow | 1 | 3 |
| K1-cp3-01 | Nasdaq-100, Russell 2000, Dow | 1 | 3 |
| K1-vxnband-01 | Nasdaq-100 | 1 | 1 |
| K1-vwap-01 | Nasdaq-100 | 1 | 1 |
| K1-predrift-01 | EXCLUDED by the lead (02:15) | - | 0 |
| ~~K1-ml-01~~ [excluded, U6] | Nasdaq-100 (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **13** = 9 port + 3 new + 1 ML. In general 3E + 3a_N + a_D. Without the Dow: 9. Nasdaq-100 only: 6 |

The cumulative program N before Stage E is 58 (design, standing inputs). K1's confirmation trials
add up to 13.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **Thin K1-specific evidence.**
   - Only 3 new members are written, and 8 budget slots are unused.
   - The log found no minute-horizon lead-lag or spread-reversion evidence inside the complex
     (containers 1 and 3). It found no directional evidence for any reconstitution day, and NKD is
     out.
   - The lead decides whether a K1 screening session is worth running with mostly port trials. The
     9 port trials sit close to the MES record (C3, C2 and C7 were null on MES).
2. **K1-predrift-01 and the "generic S&P" rule.**
   - Its mechanism is documented mainly on ES, with one robustness sentence on the E-mini Dow
     (P-K2-007-f).
   - If the lead reads it as a generic S&P mechanism, it should be cut (1 trial).
   - It is also low-frequency (about 57 confirmation events), so D4 may label it inconclusive by
     design.
3. **K1-vwap-01's rewrite and its cost fragility.**
   - The D9 floor forced a 2-minute minimum hold and a 20-entry cap onto the source's rule.
   - The source assumed no slippage, with about 15 flips a day. The lead may cut it (1 trial).
4. **K1-vxnband-01's regime filter.**
   - The cuts 20 and 30 are the source author's in-sample bucket edges, and are written as one
     trial.
   - The unfiltered variant, or variants on the Russell 2000 and the Dow, would each add trials
     (section 3).
5. **Mini halts under volatility** (F12.1: "Trading on mini-sized contracts or larger may be
   temporarily halted for affected products").
   - If D2 picks NQ, RTY or YM, a member could be untradeable exactly on high-volatility days
     (for example K1-vxnband-01's VXN >= 30 regime).
   - The lead decides whether D2 should prefer the micros for deployability, or whether the risk is
     only noted.
6. **Scope of the ISM release (D8 and D9.5a).**
   - K1-predrift-01 names ISM Services at 09:00 CT for the Dow.
   - The lead decides whether it also "concerns" NQ and RTY, for the event-window cost and the fill
     guard (C10). That would change costs for CP2, CP3, K1-vxnband-01, K1-vwap-01 and K1-ml-01.
7. **K1-ml-01's Russell leg.**
   - KF4 needs Russell 2000 bars on the research and confirmation windows even if D2 does not admit
     that exposure.
   - The lead decides whether to buy them, or to drop KF4 before any fit.
8. **Optional additions not written:**
   - the closing-auction short, X-05 (3 trials);
   - the stop-free first-candle rule, X-06 (1 trial).
9. **The Russell reconstitution calendar conflict for 2026.** November (K1-018) against December
   (K1-023) remains unresolved after fetch 6. No member depends on it.
10. **E.2 checks named in this catalog:**
    - (a) the VXN file's coverage from 2019-04-30 and Cboe's publication time (C9);
    - (b) ISM Services tables for 2019-05..2020-07, the "(EST)" reading, and continuity with the
      Non-Manufacturing name (C9);
    - (c) tick-size history 2019-2026 (C7);
    - (d) K1 price-limit tables from the rulebook chapters (C11);
    - (e) short micro histories and the full-size price-path declaration (C8);
    - (f) member-level coverage for the overnight reopen bar CP1 reads (17:00 CT) and for K1-ml-01's
      three legs.
11. **Registry hygiene** (already noted by the reader): the K1-001 DOI is wrong in the registry.

---

# Cluster K2

# Stage E.0 hypothesis catalog, cluster K2 (rates: ZT, ZF, ZN, TN, ZB, UB)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K2-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K2 is the first cluster.
> **K2 after the decisions: 8 active members, 44 confirmation trials** (5 new + 3 core ports; 18 port + 26 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K2-OpusXHigh (Stage E.0 Task 4), 2026-09-23, 21:03-21:40 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.
Written before any price, bar, tick or order-book data for any K2 product existed on this machine.
The only product-specific numbers used are contract specifications and public ADV
(reports/stage_e0_liquidity.json), Topstep's published fees and hours
(reports/stage_e0_topstep_facts.md), and event-calendar metadata: auction dates, closing times and
FOMC meeting dates. Calendar metadata carries no prices.

Inputs read in full: reports/stage_e0_research_K2.md; `[K2]` passages in the other logs (none
exist beyond K2's own log; see section 5); reports/stage_e0_source_registry.jsonl (K2 lines and
K4-008); docs/STAGE_E_DESIGN.md (D1-D15); reports/stage_e0_partition.md;
reports/stage_e0_topstep_facts.md; reports/stage_e0_liquidity.json (rates rows);
reports/stage_d1f_confirmation_list.md 2.1 A3; strategy/research/b_reference_breakout/
h1_friction_aware_opening_range_breakout.py; strategy/research/h_daily_bar/h6_prior_close_location.py;
reports/stage_d1b_family_f_declaration.md F3.3.

---

## 0. Header

| Item | Value |
|---|---|
| Products | ZT, ZF, ZN, TN, ZB, UB (CBOT Treasury futures; Topstep F1 "CME CBOT Financial/Interest Rate Futures", none starred) |
| Exposures | six, one per tenor, each with exactly one admissible contract (partition section 1): ZT, ZF, ZN, TN, ZB, UB |
| Members | 9 = 5 new + 3 core ports + 1 ML member (budget 15; 6 slots unused, see section 3) |
| Trials in N (confirmation) | 45 if D2 admits all six exposures (18 port + 26 new + 1 ML). In general 3E + 4E + E_pd + 1, where E = number of admitted exposures and E_pd = admitted exposures among {ZN, ZB}. Example: without ZB and UB, 30. |
| ML grid (research-window accounting only, D15.8) | ~~48 configurations, counted in the K2 screening session's research-window DSR for K2-ml-01~~ [superseded, U6: no ML member] |
| Starred products | none (Topstep F1: no K2 product carries "*") |
| D1 | **D1 is applied by the lead.** No K2 exposure is assumed IN. Every member below is written for all six. |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. Rule 13: ZB and UB may be outside D2's risk band at one contract; every entry marks them "traded only if D2 admits the exposure". The same condition applies to every K2 exposure (see C6). |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the one-minute ohlcv-1m bar
  whose ts_event (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its
  values are usable from then on.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine convention
  D6 and D15.3 use): "market intent on the bar at X" fills at the open of the bar at X + 1 min.
- **C3 Trade date.** Trade date d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). "Calendar
  month of d" is the month of the date d.
- **C4 Exclusions for the five new members.** The ports follow D6 as written. The new members do not
  trade on: roll-blackout dates (the program convention, `screen_candidate` with `roll_blackout`);
  dates the D10 rates calendar marks as early halt or early close (as Family H: "Days with
  early_halt_ct set: no trade"); or dates on which any bar the rule reads, or the entry bar, is
  missing or carries a different instrument_id from the entry bar (the instrument guard D6 CP1
  uses). If an exit's named bar is missing, the exit is sent on the first later bar. The engine's
  forced flatten at F is the backstop.
- **C5 Flat time.** F = 15:08 CT (D9.1; D6 rates row). No new member's last fill is later than
  15:05 CT.
- **C6 Size.** q_c of the exposure's D2 vehicle. Every K2 contract is a mini (1 lot-equivalent,
  D9.6), so D9.5's cap of 1 lot-equivalent makes q_c = 1 contract for every K2 member. At q = 1,
  D2's risk ratio is rho = r_c / R*. E.2 measures whether each exposure's r_c lies in
  [0.5 R*, 2.0 R*]. Nothing here assumes it does, for any exposure.
- **C7 Ticks and fees.** Tick size and value from reports/stage_e0_liquidity.json (CME contract
  specs, fetched 2026-09-23 20:43-20:44 PDT): ZT 0.00390625 pt = $7.8125; ZF 0.0078125 pt =
  $7.8125; ZN 0.015625 pt = $15.625; TN 0.015625 pt = $15.625; ZB 0.03125 pt = $31.25; UB
  0.03125 pt = $31.25. Topstep round turns (F3): ZT $2.32, ZF $2.32, ZN $2.62, TN $2.62, ZB $2.76,
  UB $2.92. These are 2026 specifications. E.2 must confirm that each tick size was unchanged over
  2019-05..2026-06 before any bar is read, and log any change, because CP2's buffer is in ticks.
- **C8 Price data source.** Databento GLBX.MDP3 ohlcv-1m of the vehicle (and, for K2-ml-01, of
  ZF, ZB and ZT). It is paid, bought in E.1 (D13), and available from the start-rule bound
  2019-05-06 (D4) to 2026-06-19. A bar is available at its close (C1). mbp-1 enters only through
  D8's shared five-date cost-calibration sample. No member reads order-book data.
- **C9 Event calendars (external, free, history covering 2019-05..2026-06).** Each rule reads only
  dates and scheduled clock times, never a released value (no index level, no auction result).
  - **EC-AUC, Treasury auctions.** Source: FiscalData "auctions_query" API
    (https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query).
    Queried 2026-09-23 21:05-21:13 PDT (metadata fields only, no price or result fields read).
    - **Fields read:** security_type, original_security_term, floating_rate,
      inflation_index_security, auction_date, announcemt_date, closing_time_comp ("Closing Time
      (ET) - Competitive").
    - **Availability:** these are auction-announcement fields, published on announcemt_date. A
      record counts only if announcemt_date is strictly before auction_date. Five same-day records
      exist in the 2019-05..2026-06 table and are excluded by this guard. Among the 2-, 5-, 10- and
      30-year fixed-rate nominal records, only one is affected: a 10-year reopening on 2019-06-21
      with an 11:00 ET close, announced the same day. Every retained tenor-matched record was
      announced at least 4 calendar days before its auction, so all retained fields are known
      before the trade date begins.
    - **Results fields are never read.** The same record also carries bid_to_cover_ratio,
      high_yield and other results fields.
    - **Clock:** T_a (CT) = closing_time_comp (ET) - 1 hour. Eastern and Central time change on
      the same dates.
    - **Checks for E.2:** if the announcement XML (xml_filenm_announcemt) and the query disagree
      on closing_time_comp for any auction, that auction is dropped and logged.
  - **EC-FOMC, scheduled FOMC meetings.**
    - **Source:** https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (lists 2021-2027,
      fetched 2026-09-23 21:14 PDT), plus the page's "Transcripts and other historical materials"
      for 2019-2020.
    - **Statement time 13:00 CT:** Topstep F6 table "FOMC Statement | 1:00 PM" (CT) and
      P-K2-018-c "13:00 CST".
    - **Event set:** the last day of each regularly scheduled meeting. Unscheduled meetings,
      notation votes (for example "August 22 (notation vote)" in 2025) and conference calls are
      excluded.
    - **Availability:** the schedule is published before the year begins.
  - **EC-ISM, ISM Services (Non-Manufacturing in K2-007's sample) Report On Business release
    dates.**
    - **Source:** the PR Newswire ISM newsroom
      (https://www.prnewswire.com/news/institute-for-supply-management/, WebFetch 2026-09-23
      21:10 PDT), which shows each Services PMI release stamped "10:00 ET" (for example
      "September 3, 2026, 10:00 ET"). 10:00 ET = 09:00 CT.
    - **Caveats:** WebFetch returns a paraphrase with the timestamps quoted. ISM's own calendar
      (ismworld.org rob-report-calendar) redirected to a login page and was not read. E.2 pages
      the newsroom archive back to 2019 and drops any release not stamped 10:00 ET.
  - **EC-NFP, BLS Employment Situation release dates.**
    - **Source:** https://www.bls.gov/bls/news-release/empsit.htm lists every release from January
      1994 to August 2026, with the release date in each file name (for example
      empsit_08022019). Release time "08:30 AM" (ET) is from
      https://www.bls.gov/schedule/news_release/empsit.htm, and Topstep F6 gives "Unemployment
      Rate | 7:30 AM" CT. Both fetched 2026-09-23 21:15 PDT.
  - **EC-CAL.** The D10 rates calendar (trade dates, holidays, early closes), built by E.2 from
    CME schedules.
  - **EC-NYSE.** NYSE holiday schedule, used only by K2-ml-01. It is free and published in advance.
    Not fetched in E.0, so its availability is unconfirmed here.
- **C10 Frequency (arithmetic from the calendar counts above, no price data).**
  - A member that trades on k of the ~290 eligible research-window trade dates, with zeros on
    other days (D5), needs a net P&L per event of about (290 / k) x eps_X to reach a mean of
    eps_X per trade date.
  - That multiple is about 19 to 22 for the auction members (k = 15 to 13), about 29 for the FOMC
    member (k = 10), about 19 for the ISM member (k about 15) and about 10 for the month-end
    member (k = 28).
  - These members can therefore be expected to end "null at eps" unless each event carries a
    large move. That is a legitimate funnel statement, but it is structural. See section 7,
    item 2.

---

## 1. Members

### K2-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K2. **Products read:** the traded exposure's own vehicle only. **Traded exposures
  and admissible contracts:** ZT {ZT}, ZF {ZF}, ZN {ZN}, TN {TN}, ZB {ZB}, UB {UB}, each a separate
  trial. ZB and UB are traded only if D2 admits the exposure (so is every exposure, C6).
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1
  log A10 and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1. It
  rests on no K2 passage; the K2 log holds no intraday-momentum source (section 5). D6 rule text,
  verbatim: "Signal: sign of (close of the bar at O+29 min minus open of the trade date's first
  bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the signal's
  direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
  (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
- **Instantiated with the D6 rates row (O = 07:20, C = 14:00, F = 15:08):**
  - **Signal:** close of the bar at 07:49 minus the open of the trade date's first bar (the
    Globex open, 17:00 CT on d-1).
  - **Entry:** market intent on the bar at 13:29, filling at the 13:30 open.
  - **Exit:** market intent on the first bar at or after 13:58, filling nominally at the 13:59
    open.
  - **Holding horizon:** 29 minutes. **Session window:** 13:30-13:59. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid (E.1), with
  history 2019-05..2026-06. The latest signal input, the 07:49 bar, is available at 07:50 CT, and
  the decision is at 13:30.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (= 1 contract, C6).
- **Parameters:** O+29 = 07:49, C-31 = 13:29, C-2 = 13:58 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29
  minutes. Floor: 20 entries per day ok, 2-minute minimum ok, 10-minute mean ok.
- **Falsification:** the standard condition. UCB95 of the member's mean net daily P&L per
  contract below eps_X, at >= 80% achieved null power on the confirmation window, counts against
  it. No member-specific check, because it is a port and D6 is unchanged.
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market orders only.
  3. D9.4 prohibited patterns: one trade a day, no stops, brackets or passive fills.
  4. * restriction: none applies.
  5. News: 1 lot-equivalent, which is half the 2-lot maximum. On FOMC days the position starts
     30 minutes after the 13:00 statement.
  6. Position limit: 1 contract.
  7. Price-limit proximity: no E.0 artifact establishes a CME daily limit for CBOT Treasury
     futures. If E.2's D9.7 tables find one, the harness rule applies. The catalog assumes
     nothing.
- **Data needed:** ohlcv-1m of each admitted K2 vehicle, research window 2025-04-01..2026-06-19
  and confirmation S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K2. **Products read:** own vehicle. **Exposures:** ZT, ZF, ZN, TN, ZB, UB, one
  contract each. ZB and UB (and every exposure) are traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py,
  hold_minutes = 75), as fixed in D6 row CP2. It rests on no K2 passage. D6 rule text, verbatim:
  "OR = high and low of the bars in [O, O+15 min). Entry: the first bar opening in [O+15, C) whose
  close is beyond OR_high or OR_low by at least 4 ticks of P; market intent in the break direction;
  one entry per trade date; no entry from C on. Exit: 75 minutes after the fill, or the engine's
  forced flatten at F if earlier."
  [Amended by the lead, 21:12 PDT, to D6's amended CP2 text (entry window bounded at C), answering
  this writer's note below.]
- **Instantiated:**
  - **Opening range:** the bars with open time in [07:20, 07:35).
  - **Eligible bars:** those opening in [07:35, 14:00). No entry from 14:00 CT on.
  - **Entry buffer, 4 ticks of P:** ZT 0.015625 pt, ZF 0.03125 pt, ZN 0.0625 pt, TN 0.0625 pt,
    ZB 0.125 pt, UB 0.125 pt (C7).
  - **Entry:** a close >= OR_high + buffer buys; a close <= OR_low - buffer sells.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it, or the forced
    flatten at F.
  - **Holding horizon:** 75 minutes, or less if F intervenes. **Session window:** 07:35 to F.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is
  known at 07:35 CT.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:** OR 15 minutes, buffer 4 ticks, hold 75 minutes (D6, a literal port). **Grid:**
  none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: engine flatten.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. *: none.
  5. News: 1 lot-equivalent, which may be held through a 09:00 CT release.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2, as in CP1.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 6).
- **Note for the lead (not a change; the text is copied unchanged):** [Superseded (review R-28,
  applied in Stage E.1 under U9): the lead's 21:12 amendment bounds entries at C, as the
  instantiation above states; this note predates it.] D6's text has no
  latest-entry time. On MES the gap between C (15:00) and F (15:08) was 8 minutes. On K2 it is 68
  minutes (14:00 to 15:08), so a first break after 14:00 CT can be entered here with a hold that F
  truncates. See section 7, item 1.

### K2-cp3-01 (core port CP3, prior-close location)
- **Cluster** K2. **Products read:** own vehicle. **Exposures:** ZT, ZF, ZN, TN, ZB, UB. ZB and UB
  (and every exposure) are traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3. It rests on
  no K2 passage. D6 rule text, verbatim: "Daily bar of day d from [O, C): O_d = open of the O bar,
  H and L over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules
  as Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells,
  market intent on the O bar of day d. Exit: first bar at or after C-2 min."
- **Instantiated:**
  - **Daily bar:** O_d = open of the 07:20 bar. H and L are taken over the bars opening in
    [07:20, 14:00). C_d = close of the 13:59 bar.
  - **Complete day** (Family H): the 07:20 and 13:59 bars exist, the date is not an early halt,
    and all bars in [07:20, 14:00) carry one instrument_id.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of day d's 07:20 bar.
  - **CLV:** computed in ticks, with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells
    (non-strict, as H6).
  - **Entry:** market intent on the 07:20 bar of d, filling at the 07:21 open.
  - **Exit:** first bar at or after 13:58, filling nominally at the 13:59 open.
  - **Holding horizon:** about 398 minutes. **Session window:** 07:21-13:59.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's
  bar is complete at 14:00 CT on d-1, before d begins.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 398 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: holds through the morning releases, the 12:00 CT auction closes and the 13:00 FOMC
     statement at 1 lot-equivalent, which is not the full maximum (D9.5).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-aucpre-01 (pre-auction concession)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source (NY Fed SR 1188) covers 1991-2024, overlapping the confirmation window.]
- **Cluster** K2. **Products read:** the traded vehicle; EC-AUC; EC-CAL.
- **Traded exposures (tenor-matched):** ZT on 2-year auctions; ZF on 5-year; ZN on 10-year; TN
  on 10-year; ZB on 30-year; UB on 30-year. Each exposure has one admissible contract. ZB and UB
  (and every exposure) are traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:**
  - **What is claimed:** dealers sell ahead of a Treasury auction and cover afterwards. The
    intraday trace is a V-shaped yield path centred on the auction close. Yields rise over the
    180 minutes before the close (prices fall) and reverse after the results.
  - **Verified passages:** K2-002 P-K2-002-b ("V-shaped pattern ... 0.7 to 1.2 basis points"),
    P-K2-002-c (the 180-minute pre-window definition) and P-K2-002-d. The multi-day version is
    K2-001 P-K2-001-a. Daily-frequency support that "the occurrence of an auction ... pushes
    futures prices lower" is K2-006 P-K2-006-a (abstract only).
  - **Classification:** new to the program (log tag for K2-002).
- **Event set:**
  - **Records:** EC-AUC records with security_type Note or Bond, floating_rate "No",
    inflation_index_security "No", and announcemt_date < auction_date.
  - **Tenor match:** original_security_term = "2-Year" for ZT, "5-Year" for ZF, "10-Year" for ZN
    and TN, "30-Year" for ZB and UB. Reopenings are included, because original_security_term
    carries the tenor.
  - **Mapping rule:** the permitted contract's nominal tenor, by its Topstep/CME name, equals the
    auctioned security's original term. This is a judgment. The log holds no deliverable-basket
    passage; K2-004 logged only the CTD definition, P-K2-004-a. 3-, 7- and 20-year auctions are
    therefore not traded (excluded X-06).
  - **T_a:** closing_time_comp - 1 h, in CT.
- **Entry rule:** SELL, market intent on the bar at T_a - 181 min, filling at the open of the bar
  at T_a - 180 min.
- **Exit rule:** market intent on the first bar at or after T_a - 2 min, filling at the next
  open (nominally T_a - 1 min), so the position is flat before the competitive close.
- **Holding horizon:** 179 minutes.
- **Session window by close time:**
  - 13:00 ET closes (T_a = 12:00 CT): 09:00-11:59 CT.
  - 11:30 ET closes (T_a = 10:30 CT): 07:30-10:29 CT.
  - The single 10:00 ET close (5-year, 2019-12-24): T_a = 09:00 CT, window 06:00-08:59 CT, and
    no trade if EC-CAL marks the date an early close (C4).
  - Flat by F in every case.
- **Data fields read:**
  - Vehicle ohlcv-1m open, close and instrument_id (C8), each available at its bar's close.
  - EC-AUC auction_date, closing_time_comp, original_security_term, floating_rate,
    inflation_index_security, announcemt_date. Free; 2019-2026 history confirmed by query.
    Available from announcemt_date, at least 4 days before the auction (C9).
  - EC-CAL (roll blackout, early close), known in advance.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - 180-minute window ending 1 minute before the close, from P-K2-002-c: "the difference between
    the yield observed the minute before the auction close time and that 180 minutes earlier".
  - Side SELL, from P-K2-002-b and P-K2-002-d (yields rise pre-auction).
  - **Grid:** none.
- **Expected entries and hold:**
  - One entry on each tenor-matched auction day. From the FiscalData metadata count on
    2026-09-23, before the roll-blackout, early-close and S_X exclusions:

    | Tenor | Exposures | Research window 2025-04-01..2026-06-19 | Confirmation window 2019-05-06..2024-02-29 |
    |---|---|---|---|
    | 2-year | ZT | 13 (3 at 11:30 ET) | 58 (15 at 11:30 ET) |
    | 5-year | ZF | 15 | 56 |
    | 10-year | ZN, TN | 15 | 59 |
    | 30-year | ZB, UB | 15 | 58 |

  - That is about 0.05 entries per trade date, each held 179 minutes. Floor ok. Frequency: see
    C10.
- **Falsification:**
  - The standard condition (UCB95 of mean net daily P&L per contract below eps_X at >= 80%
    achieved null power on the confirmation window counts against it).
  - **Sign check, reported beside the verdict and not a separate test:** the mechanism predicts
    a negative mean gross move of the vehicle, in ticks, from the T_a - 180 open to the T_a - 1
    open on event days. A non-negative confirmation-window mean counts against the mechanism.
- **Topstep check:**
  1. Flat by F: latest fill 11:59 CT.
  2. Order type: market.
  3. D9.4: one trade per event, no stops or brackets, no passive fill.
  4. *: none.
  5. News: flat before the auction close by design. A 07:30 or 09:00 CT release inside the
     window is held at 1 lot-equivalent, half the 2-lot maximum, which F6.3 and D9.5 allow.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles (research and confirmation windows);
  external EC-AUC and EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-aucpost-01 (post-auction recovery)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP (SR 1188, 1991-2024).]
- **Cluster** K2. **Products read:** the traded vehicle; EC-AUC; EC-CAL. **Traded exposures:** the
  same tenor match as K2-aucpre-01 (ZT 2-year, ZF 5-year, ZN and TN 10-year, ZB and UB 30-year).
  ZB and UB (and every exposure) are traded only if D2 admits the exposure. **Vehicle:** D2
  (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** the second arm of the V. After the auction result, dealers cover (buy)
    and yields fall back.
  - **Verified passages:** K2-002 P-K2-002-b, P-K2-002-c (the post-window definition: "from the
    yield observed the minute after the auction results announcement to that 180 minutes
    later") and P-K2-002-d ("reversal (-0.32 to -0.75 bps for most maturities)"). Supporting:
    K2-001 P-K2-001-a ("recover shortly thereafter").
  - **Classification:** new (log tag). This is a separate hypothesis from the pre-auction arm.
- **Event set and T_a:** as K2-aucpre-01.
- **Entry rule:** BUY, market intent on the bar at T_a + 4 min, filling at the open of the bar at
  T_a + 5 min.
- **Exit rule:** market intent on the bar at T_a + 184 min, filling at the open of T_a + 185 min,
  or the forced flatten at F if earlier.
- **Holding horizon:** 180 minutes.
- **Session window:** 12:05-15:05 CT for 13:00 ET closes; 10:35-13:35 CT for 11:30 ET closes.
  Flat by F (15:05 < 15:08).
- **Data fields read:** as K2-aucpre-01. No results field (bid-to-cover, high yield) is read.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - 180-minute hold, from P-K2-002-c.
  - **Entry lag 5 minutes after the competitive close: a judgment.** P-K2-002-c starts the
    window at "the minute after the auction results announcement". No obtainable source found
    gives a per-auction results release time: the FiscalData record carries the results but no
    release timestamp. A fixed lag therefore stands in. 5 minutes sits at the start of the
    interval over which K2-011 P-K2-011-b finds spreads back to normal ("revert to normal values
    after five to 15 minutes"). K2-002 P-K2-002-f says depth "normalize[s] quickly" after the
    auction.
  - **No leakage:** the rule reads no result, so the lag cannot leak information. On an auction
    whose results appeared after T_a + 5, the member is simply positioned before the release
    that day.
  - **Grid:** none.
- **Expected entries and hold:** as K2-aucpre-01: research 13 (ZT) or 15 (other exposures),
  confirmation 56 to 59; about 0.05 per trade date, held 180 minutes. Floor ok.
- **Falsification:** the standard condition. Sign check (reported): the mechanism predicts a
  positive mean gross move, in ticks, from the T_a + 5 open to the T_a + 185 open on event days.
- **Topstep check:**
  1. Flat by F: last fill 15:05.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: may be positioned before a late results release, at 1 lot-equivalent (not the full
     maximum).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** as K2-aucpre-01.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-fomcpost-01 (post-FOMC drift)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP (SR 1188, 1991-2024).]
- **Cluster** K2. **Products read:** the traded vehicle; EC-FOMC; EC-CAL. **Traded exposures:**
  ZT, ZF, ZN, TN, ZB, UB. ZB and UB (and every exposure) are traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "FOMC announcements are followed by a significant and persistent
    decline in yields - on the order of 0.5-1.5 bps - consistent with the previously documented
    post-FOMC drift in bond markets" (K2-002 P-K2-002-e). Falling yields mean rising futures
    prices, so the member is unconditionally long after the announcement's jump window.
  - **Why the entry waits:** K2-018 P-K2-018-c and P-K2-018-d place the announcement's co-jump
    in the 30 minutes after 13:00 CST, and its direction depends on the surprise ("17 positive
    policy surprise days ... 14 negative"). The member starts after that window, so it trades
    the drift, not the jump.
  - **Maturities:** P-K2-002-e is not split by maturity. K2-002's sample spans 2- to 30-year
    maturities (log product field), so the member covers all six tenors. K2-020 P-K2-020-a notes
    that post-FOMC return connections are amplified "except for 30-year futures". That is
    context, not a reason to drop ZB or UB.
  - **Classification:** new (log tag for K2-002).
- **Event set:**
  - The statement day of each regularly scheduled FOMC meeting (EC-FOMC). The statement must be
    released at 13:00 CT that day, a fact public at 13:00, before the 13:29 decision.
  - Unscheduled meetings, notation votes and conference calls are excluded.
- **Entry rule:** BUY, market intent on the bar at 13:29, filling at the 13:30 open.
- **Exit rule:** market intent on the bar at 15:04, filling at the 15:05 open, or F.
- **Holding horizon:** 95 minutes. **Session window:** 13:30-15:05 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m (C8).
  - EC-FOMC meeting schedule: free; the calendar page covers 2021-2027 and the historical
    materials cover 2019-2020. Available before each year.
  - Statement release at 13:00 CT (Topstep F6; P-K2-018-c): public at 13:00 CT.
  - EC-CAL.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - Entry at 13:30, after the 30-minute announcement window of P-K2-018-c.
  - **Exit at 15:05: a judgment.** It is the last fill before F. K2-002's 180-minute post-window
    would end at 16:00 CT, past F.
  - **Grid:** none.
- **Expected entries and hold:**
  - Research window: 10 statement days (Fed calendar, fetched 2026-09-23): 2025-05-07,
    2025-06-18, 2025-07-30, 2025-09-17, 2025-10-29, 2025-12-10, 2026-01-28, 2026-03-18,
    2026-04-29, 2026-06-17.
  - Confirmation window: about 38 (8 scheduled meetings a year on the calendar pages; E.2 counts
    them).
  - That is about 0.03 per trade date, held 95 minutes. Floor ok.
- **Falsification:** the standard condition. Sign check (reported): the mechanism predicts a
  positive mean gross move from the 13:30 open to the 15:05 open on event days.
- **Topstep check:**
  1. Flat by F: 15:05.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: the entry is 30 minutes after the statement. It overlaps whatever follows the
     statement that afternoon, at 1 lot-equivalent (not the full maximum).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles; EC-FOMC; EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-predrift-01 (pre-release informed-trading drift, ISM Services)
- **Cluster** K2. **Products read:** the traded vehicle; EC-ISM; EC-CAL. **Traded exposures:** ZN
  {ZN} and ZB {ZB}, the two exposures the source documents: ZN by ticker, P-K2-007-b; 30-year bond
  futures in the robustness check, P-K2-007-f. ZB (and ZN) are traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "Prices begin to move in the 'correct' direction about 30 minutes before
    the release time. The pre-announcement price drift accounts on average for about 40% of the
    total price adjustment" (K2-007 P-K2-007-a).
  - **The ZN row for this release:** ISM Non-Manufacturing, with a pre-release drift of
    "-0.044 (0.009)***" for the 10-year note per one-standard-deviation positive surprise
    (P-K2-007-d). This is the only release whose ZN drift is in a logged passage.
  - **Context passages:** bond 5-minute sd 0.04% (P-K2-007-c) and ZN median effective spread
    0.013% (P-K2-007-e).
  - **The inference, stated:** the sign of the early drift proxies the sign of the coming
    surprise, and part of the adjustment (about 60%) is still to come at and after the release.
    The rule therefore trades continuation of the early drift through the release.
  - **No consensus data:** the rule reads no survey consensus. Rule 3's proxy route is used: the
    price path itself stands in for the surprise.
  - **Classification:** new (log tag for K2-007).
  - **Not a CP1 duplicate:** CP1 is a fixed-clock, late-session trade on the overnight-plus-first-
    30-minute return. This member is event-conditioned, in a pre-release window, with a 15-minute
    hold that ends after the release.
- **Event set:** EC-ISM Services release dates, T = 09:00 CT (10:00 ET).
- **Entry rule:**
  - s = sign(close of the bar at 08:49 - open of the bar at 08:30), in ticks, that is the
    [T-30, T-11] return. If s = 0, no trade.
  - Market intent on the bar at 08:49 in direction s, filling at the 08:50 open.
- **Exit rule:** market intent on the bar at 09:04, filling at the 09:05 open (T + 5 min).
- **Holding horizon:** 15 minutes. **Session window:** 08:30-09:05 CT (signal 08:30-08:49;
  position 08:50-09:05). Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open, close and instrument_id (C8). The latest input is available at
    08:50 CT, the decision time.
  - EC-ISM release date and time: free (PR Newswire archive); release schedule published in
    advance; the index value is never read.
  - EC-CAL.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - Signal start at T-30, from P-K2-007-a ("about 30 minutes before").
  - Exit at T+5, from the paper's total-impact window "30 minutes before to 5 minutes after
    release" (log K2-007, horizon field).
  - **Signal end T-11 and entry T-10: a judgment.** This leaves the last 10 pre-release minutes
    of drift, plus the release move, to the position. It also makes the hold 15 minutes, above
    D9's 10-minute mean floor. A T-5 entry would give a 10-minute hold, exactly at that floor,
    with no margin.
  - **Grid:** none.
- **Expected entries and hold:** 1 per ISM Services release day with s != 0. That is about 15 in
  the research window and about 58 in the confirmation window (monthly; E.2 counts them from the
  archive), about 0.05 per trade date, held 15 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** hit rate P[sign(open 09:05 - open 08:50) = s] > 0.5, and the mean
    signed gross move > 0, on event days, as the mechanism predicts.
  - **Out of sample:** the paper's sample is 2008-2014 (log), so both windows here are out of
    the source's sample.
- **Topstep check:**
  1. Flat by F: 09:05.
  2. Order type: market.
  3. D9.4: one trade per event; not a stray-fill gap trade, since the entry precedes the release
     by 10 minutes.
  4. *: none.
  5. News: **holds into a scheduled release by design.** Size is 1 lot-equivalent, half the XFA
     starting maximum, so the trade is not "full Maximum Position Size directly into a scheduled
     major news event" (F6.3, D9.5). Flagged to the lead as the one K2 member that enters
     because of a release.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of ZN and ZB (research and confirmation windows); EC-ISM; EC-CAL.
- **Trials in N:** 1 per admitted exposure among {ZN, ZB} (at most 2).

### K2-monthend-01 (month-end index-extension demand, intraday slices)
- **Cluster** K2. **Products read:** the traded vehicle; EC-CAL. **Traded exposures:** ZT, ZF, ZN,
  TN, ZB, UB. ZB and UB (and every exposure) are traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **Returns side:** "Average returns are positive and highly significant in the last few days
    of the month, and are not significantly different from zero at other times" (K2-021
    P-K2-021-a). About 20 bp a month at the 10-year point (P-K2-021-b). The paper's own trade
    buys two trading days before month-end and sells at the last day's close (P-K2-021-c). The
    last-day Sharpe is close to 1, and the two-day position earns 4.5% annualized
    (P-K2-021-d). The cost benchmark is a 2-3 bp spread (P-K2-021-e).
  - **Flow side:** month-end trading concentrates at the index strike times: 3 p.m. ET until
    2021, "now largely 4:00 p.m. ET" (K2-003 P-K2-003-a/b/c/d; for example, more than a quarter
    of month-end daily activity falls in 3:45-4:15 p.m. ET in 2025).
  - **How the member uses them:** the two-day hold is infeasible under flat-by-F (X-04). The
    member takes the day-session slice of each of the two days the paper holds, and exits after
    the later strike time.
  - **Classification:** port of D.1 family E (calendar/events; the log's tag for K2-003 and
    K2-021), written on K2's own clock. It is not one of D6's core ports; D6 ports no family E
    member.
- **Event set:** N = the last trade date of each calendar month in EC-CAL, and N-1 = the trade
  date before it. Both are traded, each independently (C4 applies per date).
- **Entry rule:** BUY, market intent on the bar at 07:20 (O), filling at the 07:21 open.
- **Exit rule:** market intent on the bar at 15:04, filling at the 15:05 open, or F.
- **Holding horizon:** 464 minutes. **Session window:** 07:21-15:05 CT. This covers the pre-2021
  strike (3 p.m. ET = 14:00 CT) and the later one (4 p.m. ET = 15:00 CT), so no date switch is
  needed. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL trade dates, known
  in advance.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - Days N-1 and N, from P-K2-021-c.
  - **Entry at O: a judgment.** K2-003's flows are cash-session flows, measured over
    "7:00 a.m.-5:30 p.m. ET", with the strike times inside the day. D9's member-level coverage
    check is built for the day session. The Globex-night part of each day is not held.
  - **Exit at 15:05:** after the 15:00 CT strike and the last fill before F.
  - **Grid:** none.
- **Expected entries and hold:**
  - Two entries a month: 28 in the research window (April 2025 to May 2026; June 2026's last
    dates fall after 2026-06-19) and 116 in the confirmation window (May 2019 to February 2024).
    These counts are before exclusions.
  - That is about 0.1 per trade date, held 464 minutes. Floor ok.
  - **Roll interaction:** K2-005 places the quarterly roll in the days before First Intention
    Day. Month-end dates that E.2's roll table blacks out are dropped, not moved.
- **Falsification:** the standard condition. Sign check (reported): positive mean gross move
  from the 07:21 open to the 15:05 open on event days. Days N and N-1 are reported separately
  (descriptive).
- **Topstep check:**
  1. Flat by F: 15:05.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: holds through any same-day release at 1 lot-equivalent (not the full maximum).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles (research and confirmation windows); EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**
- **Traded vehicle: ZN.**
  - **Reason:** ZN is the single K2 exposure the log documents most often:
    - K2-007 (ZN by ticker, P-K2-007-b);
    - K2-017 (the 10-year note futures, P-K2-017-a);
    - K2-018 (TY in the curve, P-K2-018-b);
    - K2-011 (10-year note, P-K2-011-c/e);
    - K2-021 (10-year figure, P-K2-021-b).
    It also has the highest public ADV in the cluster: 2,589,058 contracts per day, YTD 2026
    (liquidity JSON).
  - **Fallback, declared now so it is not chosen later:** if D2 does not admit ZN, the vehicle is
    ZF (K2-008's 5-year, P-K2-008-e; K2-020's 5-year transmitter, P-K2-020-a). If D2 admits
    neither, the lead decides.
- **Products the features read:** ZN (vehicle), ZF, ZB and ZT. Their bars are needed even where
  an exposure is not traded (D2: a non-traded exposure may serve as a leg). The calendars read
  are EC-FOMC, EC-AUC, EC-NFP, EC-ISM, EC-CAL and EC-NYSE.
- **Cluster features.** There are 7; together with D15.4's B1-B5 that makes 12. For every
  feature, t_j is the decision time, and "bar at t_j - 1 min" is the last bar closed at t_j.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| K1 | fomc_post | 1 if d is the statement day of a regularly scheduled FOMC meeting on the schedule published before d, and t_j >= 13:00 CT; else 0 | K2-002 P-K2-002-e; K2-018 P-K2-018-c, P-K2-018-d | schedule known in advance (EC-FOMC); depends only on the clock |
| K2 | auction_phase | Over EC-AUC records with auction_date = d, security_type Note or Bond, floating_rate "No", inflation_index_security "No", original_security_term in {2-, 5-, 7-, 10-, 20-, 30-Year} (K2-002's maturity set) and announcemt_date < d. The value is +1 if some record has T_a <= t_j < T_a + 180 min; else -1 if some record has T_a - 180 min <= t_j < T_a; else 0 | K2-002 P-K2-002-b, P-K2-002-c, P-K2-002-d; K2-001 P-K2-001-a; K2-006 P-K2-006-a | announcement fields, published on announcemt_date, before d (C9); no result field read |
| K3 | month_end | 2 if d is the last trade date of its calendar month in EC-CAL; 1 if it is the second-to-last; else 0 | K2-021 P-K2-021-a, P-K2-021-c, P-K2-021-d; K2-003 P-K2-003-c, P-K2-003-d | calendar known in advance |
| K4 | release_min | On d, let tau be the latest scheduled release time <= t_j among the Employment Situation (07:30 CT, EC-NFP) and ISM Services (09:00 CT, EC-ISM) releases scheduled for d. The value is min(t_j - tau, 120) in minutes if such tau exists; else -1 | K2-008 P-K2-008-b, P-K2-008-c, P-K2-008-d ("volatility for 40 minutes and slight effects for several hours"); K2-011 P-K2-011-a, P-K2-011-b; K2-006 P-K2-006-b (NFP and ISM_NonM listed); K2-007 P-K2-007-d; Topstep F6 (07:30 CT) | release schedules known in advance; depends only on the clock |
| K5 | zf_ret30 | (close of the ZF bar at t_j - 1 min - open of the ZF bar at t_j - 30 min) / 0.0078125, in ZF ticks. Both bars must exist with one ZF instrument_id, else no trade at t_j. With the ZF fallback vehicle, this reads ZN instead (/ 0.015625) | K2-020 P-K2-020-a (the 5-year's "central information-transmitting role"); K2-008 P-K2-008-e | ZF bar closes <= t_j |
| K6 | curve_ret30 | 10^4 x [ln(ZB close_{t_j - 1 min} / ZB open_{t_j - 30 min}) - ln(ZT close_{t_j - 1 min} / ZT open_{t_j - 30 min})], using the same bar convention as K5. Each leg's two bars must exist with one instrument_id, else no trade at t_j | K2-018 P-K2-018-a, P-K2-018-d (co-jumps and level shifts across the curve); K2-020 P-K2-020-a (cross-tenor return connections) | ZB and ZT bar closes <= t_j |
| K7 | eqopen_ret | If d is an NYSE trading day and t_j >= 09:00 CT: (close of the vehicle's 08:59 bar - open of its 08:30 bar) / vehicle tick. If t_j <= 08:30 CT, or the NYSE is closed on d: 0. This 0 is a fixed literal because the window has not happened; it is not an imputation, and a missing 08:30 or 08:59 bar means no trade | K2-017 P-K2-017-a, P-K2-017-b ("more informative for permanent price changes in the 30-min period after the US stock market opens"; placebo on US holidays) | 09:00 CT, from the vehicle's own bars; NYSE holidays published in advance |

- **Decision window [W0, W1] = [07:30, 14:30] CT; horizon h = 30 minutes.**
  - Decision times are t_j = 07:30, 08:00, ..., 14:30, which is 15 a day. W1 + h = 15:00 <= F.
  - **Why this window:** every scheduled K2 event in the log falls on a :00 or :30 CT boundary.
    That covers the 07:30 releases, the 09:00 ISM release, the auction closes (10:30, and 12:00
    for 13:00 ET), the 13:00 FOMC statement, and the 14:00 and 15:00 index strikes. Each event
    minute therefore coincides with a decision time.
  - **Consequence of D15.3's fill convention:** a position covers [t_j + 1 min, t_j + h] and
    exits at the open of t_{j+1}. The member is therefore flat during the first minute of every
    event, which is the minute K2-011 P-K2-011-b says carries the adjustment ("generally occurs
    within one minute"). It trades the post-event dynamics, never the jump.
  - **Why h = 30:** it is the horizon over which the logged responses play out. K2-007's drift
    runs over the 30 minutes before a release (P-K2-007-a). K2-017's window is the 30 minutes
    after the equity open (P-K2-017-b). K2-018 uses a 30-minute post-FOMC window (P-K2-018-c).
    K2-008 finds volatility elevated for about 40 minutes (P-K2-008-d).
    - h = 15 would sit inside the 5-15 minute widened-spread period (P-K2-011-b).
    - h = 60 or 120 would average across consecutive events (07:30 then 09:00; 12:00 then
      13:00).
- **Expected rows:** about 4,350 in the research window: 15 per eligible trade date x about 290
  eligible dates, after the roll-blackout, vendor-degraded and early-halt exclusions of D15.3.
  E.2 gives the exact count.
- **Expected entries:** at most 15 per day (<= 20), each held 30 minutes. Floor ok by
  construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps
  at >= 80% achieved null power on the confirmation window counts against it). Failing the D5
  screen puts it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 15:00.
  2. Order type: market (D15.6).
  3. D9.4: at most 15 entries a day, 30-minute holds, no stops or brackets.
  4. *: none.
  5. News: q_c = 1 lot-equivalent, not the full maximum. The member is also flat in the first
     minute of every :00/:30 scheduled event.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of ZN, ZF, ZB and ZT. The research window is used for training and
  tuning, the confirmation window for the frozen model. External data: EC-FOMC, EC-AUC, EC-NFP,
  EC-ISM, EC-CAL, EC-NYSE.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48
  (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K2-scalp-01 | ZB scalping: about 10 trades per session targeting 8 ticks and averaging about 1 tick (K2-012 P-K2-012-b, P-K2-012-c) | D9.4 prohibited patterns; rule 4 (orders) | "Running scalping algorithms designed to exploit unrealistic SIM fills" [F7.2]. The edge rests on passive fills and queue position at about 1 tick per trade. The performance claims are vendor-asserted and unverified (P-K2-012-c). |
| X-02 K2-hftbook-01 | ZB quote-level fair-price trading with order-book and cash-futures cointegration features (K2-019 P-K2-019-a) | D9.4; rule 4 (market orders only); data | The benefit is cost reduction versus a one-tick spread, which needs passive order placement and queue priority. Its inputs are quote-level cash and futures books, which the program does not hold. |
| X-03 K2-auc5d-01 | Short 5 days before an auction, long 5 days after (K2-001 P-K2-001-a, P-K2-001-b, P-K2-001-c) | Flat by F | Multi-day positions. The same-day slice is K2-aucpre-01 and K2-aucpost-01. |
| X-04 K2-eom2d-01 | Long from the close two trading days before month-end to the last day's close (K2-021 P-K2-021-c) | Flat by F | Two-night hold. The day-session slices are K2-monthend-01. |
| X-05 K2-basis-01 | Cash-futures basis trade (K2-009 P-K2-009-a, P-K2-009-b, P-K2-009-c) | Flat by F; tradability | Multi-quarter repo-financed position with a cash Treasury leg that is not tradable on Topstep. The source is descriptive, with no signal. |
| X-06 K2-aucother-01 | The auction V (K2-002) traded on 3-, 7- and 20-year auctions, or on TIPS and FRN auctions | Rule 1 (sourcing) | No permitted contract carries those nominal tenors. Mapping them to ZT, ZF, ZN or ZB would need deliverable-basket facts the log does not hold (K2-004 logged only the CTD definition, P-K2-004-a). TIPS and FRNs are outside K2-002's nominal-coupon sample (log product field). These auctions do enter K2-ml-01's auction_phase feature (7-, 20-year) as a clock input, which needs no mapping. |
| X-07 K2-btc-01 | Trade the futures on the bid-to-cover ratio after the results: a high ratio raises futures prices (K2-006 P-K2-006-a) | Rule 3 (data availability and look-ahead); intraday evidence | No confirmed source gives a per-auction results publication time (FiscalData carries results with no release timestamp), so no decision time can be proven to follow publication. With a lag long enough to be safe, only a daily-frequency effect is documented, and only in an abstract; the log has no intraday post-result drift. |
| X-08 K2-surprise-01 | Trade the post-release move signed by the announcement surprise (K2-011 P-K2-011-a; K2-015 P-K2-015-a; K2-008 P-K2-008-b) | Rule 3 (proprietary data); evidence for the proxy | The surprise needs consensus surveys (Bloomberg or MMS). No named, obtainable historical source was found in E.0. The obtainable proxy, the first minutes' price response, leaves nothing documented to trade: "the adjustment to news generally occurs within one minute" (P-K2-011-b), and no post-jump drift is in the log. The one documented drift, pre-release, is K2-predrift-01. |
| X-09 K2-rollspread-01 | Trade the calendar spread, or the legs, during the quarterly roll (K2-005 P-K2-005-a, P-K2-005-b, P-K2-005-c, P-K2-005-d) | D9.4; D2 vehicle; roll blackout | The documented effect is pro-rata passive fill allocation, an execution effect that depends on resting orders. The spread is not an exposure's D2 vehicle. The program removes roll-blackout dates. |

---

## 3. Beyond budget (lead decides)

None. The log supports 5 new members inside the budget of 11. Three candidates were considered
and not written:
- **Extending K2-predrift-01 to the other drift announcements.** K2-007's abstract says "Nine of
  the 20 announcements that move markets show evidence of substantial informed trading"
  (P-K2-007-a), but the nine are not in any logged passage. This is insufficient evidence in the
  log, not a budget overflow. The lead decides whether to have those passages logged (section 7,
  item 4).
- **A strike-window-only month-end member.** K2-003 documents volume, not price direction:
  insufficient evidence.
- **A last-day-only month-end variant.** It is the paper's sub-result, already inside
  K2-monthend-01's day N.

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Sharma (arXiv:1705.08022), "Using Macroeconomic Forecasts to Improve Mean Reverting Trading Strategies" (K2 log section 4; no registry id) | K2 10-year Treasury yield signal -> K3 FX pairs | the 10-year yield used as a forecast input to trade FX |
| Alquist, Ellwanger, Jin (2020), K4-008 (registry tags K4, K1, K2, K3) | K4 oil-inventory news -> K2 Treasury futures (and K1, K3) | one cluster's announcement response on another's product; K4 already flagged it; no K2 passage was ever logged |

---

## 5. Log accounting

Every passed item in reports/stage_e0_research_K2.md, and every `[K2]`-tagged passage elsewhere.

| Item | Disposition |
|---|---|
| K2-001 Lou, Yan, Zhang | Supporting evidence in K2-aucpre-01, K2-aucpost-01 and K2-ml-01 (P-K2-001-a). The literal multi-day strategy is not intraday-feasible: X-03. |
| K2-002 Fleming, Liu, Nguyen (SR1188) | Used: K2-aucpre-01 and K2-aucpost-01 (P-b, c, d, f); K2-fomcpost-01 (P-e); K2-ml-01 auction_phase and fomc_post. |
| K2-003 Dyer, Fleming, Shachar | Used: K2-monthend-01 (exit timing and flow side, P-a to d); K2-ml-01 month_end. A strike-window-only member is insufficient evidence (volume, not price; section 3). |
| K2-004 CME "Understanding Treasury Futures" | Reference only, with no mechanism. P-K2-004-a is cited for why the tenor mapping stops at nominal tenors (X-06). |
| K2-005 Quantitative Brokers roll | Excluded, X-09 (execution and pro-rata fills, the roll blackout, not a vehicle). P-K2-005-d informs no rule. |
| K2-006 / K2-014 Smales (duplicate registry lines; one source) | Daily-frequency supporting evidence for K2-aucpre-01 (P-a). P-b lists NFP and ISM_NonM, supporting K2-ml-01 release_min. The bid-to-cover direction is excluded, X-07. Not intraday-feasible as documented (daily, abstract only). The duplicate registry id is left for the lead. |
| K2-007 Kurov, Sancetta, Strasser, Wolfe (panel K1/K2) | Used: K2-predrift-01 (P-a to f); K2-ml-01 release_min (P-d). The `[K1]` passages belong to K1's CatalogWriter. |
| K2-008 Fleming, Remolona | Used: K2-ml-01 release_min (P-b, c, d) and zf_ret30 (P-e). No directional member: the documented pattern is volatility, volume and spread, not direction (part of X-08). |
| K2-009 Mixon, Orlov (CFTC) | Excluded, X-05. Not intraday-feasible. |
| K2-010 Bodor, Carlier (Eurex Bund LOB) | Not ported: D.1 family A. D6 does not port family A, and the documented pattern is non-directional activity seasonality whose Eurex timing does not transfer (log quality note). Insufficient evidence for a K2 rule. |
| K2-011 Balduzzi, Elton, Green | Used for timing: K2-aucpost-01 (P-b, the entry lag) and K2-ml-01 (the h choice and release_min, P-a, b). The surprise-response member is excluded, X-08. |
| K2-012 Kinlay | Excluded, X-01. |
| K2-013 Dujava (Quantpedia) | Not intraday-feasible: monthly signals and rebalancing on end-of-month closes (P-K2-013-b). Not covered by any port; CP3 is a prior-day CLV rule, not a multi-week trend. |
| K2-015 Andersen, Bollerslev, Diebold, Vega (panel K1/K2/K3) | The surprise-response member is excluded, X-08. P-a and P-c support K2-ml-01's event-clock design. The `[K1]` and `[K3]` passages belong to those clusters. |
| K2-016 Brandt, Kavajecz, Underwood | Insufficient evidence: abstract only, a cash-futures order-flow description with no directional rule, and P-K2-016-b is itself unverified. |
| K2-017 Indriawan, Jiao, Tse | Used: K2-ml-01 eqopen_ret (P-a, b). A directional member is insufficient evidence: abstract only, and "more informative for permanent price changes" does not predict a drift. |
| K2-018 Barunik, Fiser | Used: K2-fomcpost-01 entry timing (P-c, d); K2-ml-01 fomc_post and curve_ret30 (P-a, d). No directional member: the co-jump direction depends on the surprise (P-d). |
| K2-019 Decrem et al. | Excluded, X-02. |
| K2-020 Chen, Fu, Yang | Used: K2-ml-01 zf_ret30 and curve_ret30 (P-a). A directional tenor lead-lag member is insufficient evidence: abstract only, and it documents volatility transmission and contemporaneous connections, not a signed lead-lag. |
| K2-021 Hartley, Schwarz | Used: K2-monthend-01 (P-a to e); K2-ml-01 month_end. The literal two-day hold is excluded, X-04. |
| K2-022 Zhang, Hung, Chiu | Not intraday-feasible as documented, and insufficient evidence: abstract only, volatility timing with periodic rebalancing. D-family gates are not ported (D6). K2-ml-01's common B4 carries volatility state. |
| Sharma (K2 log section 4) | Routed to K8. |
| K4-008 (registry, tagged K2) | Routed to K8 (K4's flag). No `[K2]` passage exists; K4 did not read it past the pre-filter. |
| `[K2]` search in the other logs (K3, K3 partial, K4 shallow, K5, K5 partial) | No `[K2]`-tagged passage. The mentions of K2 are rejection or flag lines: R-K5-003 (Kurov is K1/K2 territory, already K2-007), the K3 and K4 lines on K4-008, and K5's dollar and rates against gold (K8). Nothing to use. |
| R-K2-001 to R-K2-006; Carver and Robot Wealth (unreached) | Not passed items. Rejected at the pre-filter, or unread by the reader. Not used. |

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all six admitted) |
|---|---|---|---|
| K2-cp1-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-cp2-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-cp3-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-aucpre-01 | ZT, ZF, ZN, TN, ZB, UB (tenor-matched) | 1 | 6 |
| K2-aucpost-01 | ZT, ZF, ZN, TN, ZB, UB (tenor-matched) | 1 | 6 |
| K2-fomcpost-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-predrift-01 | ZN, ZB | 1 | 2 |
| K2-monthend-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| ~~K2-ml-01~~ [excluded, U6] | ZN (fallback ZF) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **45** (18 port + 26 new + 1 ML). With E admitted exposures and E_pd admitted among {ZN, ZB}: 7E + E_pd + 1. Without ZB and UB: 30. |

---

## 7. Open items for the lead (decisions reserved to the lead; none taken here)

1. **CP2 has no latest-entry time.** [Superseded (review R-28, U9): the lead's 21:12 amendment
   bounds entries at C.] It is copied verbatim from D6. On K2, C = 14:00 and
   F = 15:08, so a first break between 14:00 and 15:08 can be entered and then cut short by F.
   On MES the equivalent gap was 8 minutes. The lead decides whether the port needs a
   latest-entry time to remain the MES family.
2. **Event-member frequency (C10).** The four event members, 26 trials, trade on about 3% to 10%
   of dates. By arithmetic they need about 10 to 29 x eps_X per event to reach eps_X a day, so
   they are likely to yield "null at eps". That is informative for the funnel but costs trials in
   N. The lead decides whether they stay at one trial per exposure, are pooled, or are cut.
3. **D2 at the 1-lot cap.** Every K2 member trades exactly 1 contract (C6), so D2's band reduces
   to r_c / R* in [0.5, 2.0]. Exposures below the band are possible as well as ZB and UB above
   it. E.2 measures; the catalog assumes neither.
4. **K2-007's nine drift announcements are not logged.** Extending K2-predrift-01 beyond ISM
   Services needs those passages logged first, by a reader follow-up. The full text was fetched
   by the K2 reader.
5. **Duplicate registry lines K2-006 and K2-014** (the same Smales paper), and K2-006's
   "authors: unspecified". Registry hygiene, for the lead.
6. **E.2 checks named in this catalog:**
   - tick-size history for 2019-05..2026-06 (C7; CP2's buffer);
   - the FiscalData announcement against the query for closing_time_comp (C9);
   - paging the PR Newswire ISM archive and re-verifying each 10:00 ET stamp (WebFetch gave a
     paraphrase);
   - the FOMC 2019-2020 schedule from the Fed's historical pages;
   - whether CBOT Treasury futures carry any CME daily price limit (D9.7);
   - the roll-blackout interaction with month-end and late-month auction dates.
7. **Mapping judgments the lead may narrow.** TN is mapped to 10-year auctions and UB to 30-year
   auctions, by the contracts' nominal tenor. K2-predrift-01 is limited to {ZN, ZB} by the
   source's product list.
8. **The ML vehicle's fallback order** (ZN, then ZF) is declared in K2-ml-01. The lead may
   overrule it before E.2.

---

# Cluster K3

# Stage E.0 hypothesis catalog, cluster K3 (FX: 6E, E7, M6E, 6A, M6A, 6B, M6B, 6C, 6J, 6S, 6N)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K3-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U7: M6E and M6A stay non-candidates for D2 until Topstep answers the user's support email (D2, D9.8).
> **K3 after the decisions: 9 active members, 31 confirmation trials** (6 new + 3 core ports; 21 port + 10 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K3-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:15 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K3 product (or any equity index) existed on this machine. It uses only these product-specific
numbers:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- calendar metadata: bank-holiday and national-holiday lists, TARGET closing days, fix clock times.

No price level, range or volatility of any product is used or assumed anywhere below.

**Inputs read in full:**
- reports/stage_e0_research_K3.md (the superseded sonnet log was not used).
- Every `[K3]`-tagged passage elsewhere: K2-015 (Andersen, Bollerslev, Diebold, Vega) in
  reports/stage_e0_research_K2.md. No other log holds a `[K3]` tag (grep over all
  reports/stage_e0_research_K*.md).
- reports/stage_e0_source_registry.jsonl (K3 lines, K2-015, K4-008).
- docs/STAGE_E_DESIGN.md D1-D15 with the 21:12 and 21:52 amendments; reports/stage_e0_STATE.md rulings.
- reports/stage_e0_partition.md; reports/stage_e0_topstep_facts.md (F1-F12);
  reports/stage_e0_liquidity.json (K3 rows).
- reports/stage_d1f_confirmation_list.md 2.1 A3; strategy/research/b_reference_breakout/
  h1_friction_aware_opening_range_breakout.py; strategy/research/h_daily_bar/h6_prior_close_location.py.
- reports/stage_e0_catalog_K2.md and reports/stage_e0_catalog_K4.md, for format only.

**Official pages fetched in this task** (curl, 2026-09-24 01:22-01:30 PDT; saved under the
scratchpad `fetch/` folder). Fetched only to confirm fix times and calendar sources; no mechanism
research was done:
- https://www.gov.uk/bank-holidays.json (HTTP 200). England-and-Wales events 2019-01-01 to 2028,
  83 events, including the ad hoc ones (for example 2022-09-19).
- https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv (HTTP 200, Shift-JIS). Japanese national
  holidays 1955-2027.
- https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
  (HTTP 200), verbatim: "The reference rates are usually updated at around 16:00 CET every working
  day, except on TARGET closing days . They are based on the daily concertation procedure between
  central banks across Europe, which normally takes place around 14:10 CET."
- https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html (HTTP 200). It marks
  "* : TARGET closing day" on "New Year's Day*", "Good Friday*", "Easter Monday*", "Labour Day*",
  "Christmas Day*", "Christmas Holiday* 26 December", listed for 2026, 2027 and 2028.
- HEAD requests only, no body read (the bodies are equity-index price histories):
  - STOXX h_3msx5e.txt: the certificate chain was rejected from this machine. A Wayback capture exists:
    HEAD on web.archive.org/web/2025/... returned 302.
  - FRED series NIKKEI225: no response (HTTP/2 stream error).
  - indexes.nikkei.co.jp/en/nkave/archives/data: 403 to curl.
  - msci.com/end-of-day-data-search: 200 with an empty body on HEAD.

  None of these confirms that a free history is available (see K3-mehedge-01).

**Time-zone conversions** were computed locally with Python zoneinfo (the IANA tz database). No
network was used for them.

---

## 0. Header

| Item | Value |
|---|---|
| Products | 6E, E7, M6E*, 6A, M6A*, 6B, M6B, 6C, 6J, 6S, 6N (CME; Topstep F1). 6M is on the permitted list but out of the traded universe |
| Exposures IN | EUR {6E, E7, M6E}; AUD {6A, M6A}; GBP {6B, M6B}; CAD {6C}; JPY {6J}; CHF {6S}; NZD {6N} (design D1 table) |
| **D1 applied: 6M out** | MXN (6M) fails D1(b): coverage 0.903 < 0.95. No member trades or reads it |
| Members | **10 = 6 new + 3 core ports + 1 ML member.** Budget 15, so 5 slots are unused (section 3) |
| Trials in N (confirmation) | **36 if D2 admits all seven exposures:** 21 port + 14 new + 1 ML. The general formula is in section 6 |
| ML grid | ~~48 configurations, counted only in the K3 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Starred products | **M6E and M6A: restriction UNRESOLVED** (D9.8; topstep facts F12.1: "no product-specific restriction naming them was found"). Every EUR and AUD member carries the flag. M6B is not starred |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. CAD, JPY, CHF and NZD have one full-size contract each (q = 1). EUR, AUD and GBP may go to a micro (q <= 10) if the full-size contract fails rho <= 2.0. Every entry is written for the exposures its evidence names, each **traded only if D2 admits the exposure** |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the one-minute ohlcv-1m bar whose
  ts_event (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values are
  usable from then on. "The bar at T - k" means the bar whose open is k minutes before clock time T.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine convention
  of D6 and D15.3). "Market intent on the bar at X" fills at the open of the bar at X + 1 min.
- **C3 Trade date.** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). CME FX reopens at
  17:00 CT and Topstep allows trading from "Weekday reopen | 5:00 PM CT" (F4). So a position opened
  after 17:00 CT on calendar day d-1 and closed before 15:08 CT on d lies inside one trade date and
  holds nothing across the daily close. The overnight members below (K3-tkypre-01, K3-tkypost-01,
  K3-ecbfix-01's first leg, K3-ml-01's early decisions) rely on this.
- **C4 Exclusions for the six new members.** The ports follow D6 as written. A new member does not
  trade on:
  - roll-blackout dates (program convention, `screen_candidate` with `roll_blackout`);
  - dates the D10 FX calendar marks as early halt or early close ("Days with early_halt_ct set: no
    trade", Family H);
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which the bars of one
    signal computation or of one position carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
  flatten at F is the backstop.
- **C5 Flat time.** F = 15:08 CT (D9.1; D6 FX row: O = 07:20, C = 14:00, F = 15:08). No new member's
  last fill is later than 15:05 CT. C = 14:00 CT agrees with CME's "Daily Settlement 2:00 p.m. Central
  Time" (R-K3-015, CME FX Markers page, verbatim in the K3 log).
- **C6 Size.** q_c of the exposure's D2 vehicle, at most 1 lot-equivalent (D2 as amended 21:12;
  D9.5).
  - **Lot weights (D9.6):** 6E, 6A, 6B, 6C, 6J, 6S and 6N count 1 each.
  - **M6E, M6A, M6B:** 0.1 each. This is inferred from Topstep's general 10:1 micro rule; no page
    names them (F12.4).
  - **E7:** counted 1 here, as a non-micro. It is named in no Topstep weighting table (F12.4), so E.2
    confirms.
  - So q_c = 1 for a full-size vehicle or E7, and q_c <= 10 for a micro. No member sizes by signal.
- **C7 Ticks and fees.** From reports/stage_e0_liquidity.json (CME contract specifications, fetched
  2026-09-23 20:44-20:46 PDT) and Topstep F3 round turns:

  | Contract | Exposure | Tick | Tick value | Topstep round turn | Lot-equivalent |
  |---|---|---|---|---|---|
  | 6E | EUR | 0.00005 | $6.25 | $4.22 | 1 |
  | E7 | EUR | 0.0001 | $6.25 | $2.72 | 1 (E.2 confirms) |
  | M6E* | EUR | 0.0001 | $1.25 | $1.00 | 0.1 (inferred) |
  | 6A | AUD | 0.00005 | $5.00 | $4.22 | 1 |
  | M6A* | AUD | 0.0001 | $1.00 | $1.00 | 0.1 (inferred) |
  | 6B | GBP | 0.0001 | $6.25 | $4.22 | 1 |
  | M6B | GBP | 0.0001 | $0.625 | $1.00 | 0.1 (inferred) |
  | 6C | CAD | 0.00005 | $5.00 | $4.22 | 1 |
  | 6J | JPY | 0.0000005 | $6.25 | $4.22 | 1 |
  | 6S | CHF | 0.00005 | $6.25 | $4.22 | 1 |
  | 6N | NZD | 0.00005 | $5.00 | $4.22 | 1 |

  These are 2026 specifications. E.2 must confirm that each tick was unchanged over 2019-05..2026-06
  before any bar is read, because CP2's buffer and several ML features are in ticks.
- **C8 Price data.** Databento GLBX.MDP3 ohlcv-1m of the vehicle.
  - **Cost and timing:** paid. The research window is bought in E.1, and the confirmation and
    holdout-2 history of the chosen vehicle in E.2b (D13; K3 quoted $14.24 research, $41.25-49.34
    step 2, $4.18 mbp-1).
  - **History:** the micros were listed on 2009-03-23 (liquidity JSON), so every K3 contract has
    2019-05..2026-06 history. E7's listing date is not in the JSON; E.2 confirms it.
  - **Availability:** a bar is available at its close (C1).
  - **Tick-free signals:** every new-member signal uses a price difference only through its sign, or
    a percent return, so it gives the same decision on any contract of an exposure.
  - **mbp-1** enters only through D8's shared five-date cost sample. No member reads order-book data.
  - **Quotation:** every K3 contract is quoted in U.S. dollars per unit of the foreign currency ("All
    these foreign exchange contracts are denominated in U.S. dollars per unit of the foreign currency",
    P-K3-007-b). A rise in 6J is a fall in USD/JPY.
- **C9 Fix clocks and calendars.** All are external, free, and known before the trade date. No rule
  reads a fix value, a reference rate or any published price.
  - **T_L(d), the WM/Reuters London 4 p.m. fix.**
    - **Definition:** 16:00 Europe/London on the calendar date of d, converted to America/Chicago
      with the IANA tz database.
    - **Conversion rule:** 16:00 London = 10:00 CT, except in the weeks when the US is on daylight
      time and the UK is not. Those run from the second Sunday of March to the day before the last
      Sunday of March, and from the last Sunday of October to the day before the first Sunday of
      November; in them T_L = 11:00 CT.
    - **Computed weekday ranges at 11:00 CT:** 2019-03-11..03-29, 2019-10-28..11-01,
      2020-03-09..03-27, 2020-10-26..10-30, 2021-03-15..03-26, 2021-11-01..11-05, 2022-03-14..03-25,
      2022-10-31..11-04, 2023-03-13..03-24, 2023-10-30..11-03, 2024-03-11..03-29, 2024-10-28..11-01,
      2025-03-10..03-28, 2025-10-27..10-31, 2026-03-09..03-27.
    - **Sources:** "the London fix at 4:00 p.m. local time (or 11:00 a.m. ET)" (P-K3-016-c); "The
      11am spike is likely related to the WM/Reuters spot foreign exchange fixing, which is at 4pm
      London time" (P-K3-032-a).
  - **T_E(d), the ECB reference-rate fix.**
    - **Definition:** 14:15 Europe/Berlin (CET/CEST) on the date of d, converted to CT.
    - **Conversion rule:** 07:15 CT, except in the same mismatch weeks as T_L (EU and UK clocks change
      on the same dates; computed), when it is 08:15 CT.
    - **Sources:** "the 'ECB fix' at 8:15 a.m. ET (2:15 p.m. local time)" (P-K3-016-c). The ECB page
      fetched above says the concertation "normally takes place around 14:10 CET". The source's
      14:15 is used because it is the end of the source's own strategy window (P-K3-016-d).
  - **T_T(d), the Tokyo 9:55 JST fix.**
    - **Definition:** 09:55 Asia/Tokyo on the Tokyo calendar date that carries d's date label.
      Japan has no daylight time.
    - **In CT:** it falls on the previous CT evening, **18:55 CST or 19:55 CDT on calendar day d-1**,
      which is inside trade date d (C3).
    - **Computed examples:** Tokyo 2025-01-10 09:55 = 2025-01-09 18:55 CST; Tokyo 2025-03-10 = 2025-03-09
      19:55 CDT (the US is already on daylight time); Tokyo 2025-07-10 = 2025-07-09 19:55 CDT.
    - **Sources:** "if the switching time is at the moment of the Tokyo fixing (00:55GMT)"
      (P-K3-022-c); "at 9:55 a.m. local time which is 8:55 p.m. ET (or 7:55 p.m. depending on
      daylight saving time (DST))" (P-K3-016-c).
  - **E.2 known-answer tests for the three clocks:**
    - T_L: 2025-03-10 is 11:00; 2025-03-31 is 10:00; 2025-10-27 is 11:00; 2025-11-03 is 10:00;
      2021-11-01..05 are 11:00.
    - T_E: 2025-03-10 is 08:15; 2025-04-01 is 07:15.
    - T_T: for d = 2025-11-04 it is 2025-11-03 18:55 CT.
  - **EC-EW, England-and-Wales bank holidays.** gov.uk JSON (fetched), free, covering 2019-2028. Each
    holiday is announced before its date.
  - **EC-JP, Tokyo business day.**
    - **Definition:** a weekday that is not a national holiday in the CAO CSV (fetched; 1955-2027) and
      is not 31 December, 1 January, 2 January or 3 January.
    - **The year-end rule is a judgment:** the Japanese banks' year-end closure is not in any logged
      passage. E.2 may check it against any free record of which dates carried a Tokyo fix.
  - **EC-TGT, TARGET closing days.** The six "*" days on the ECB working-hours page (fetched). The page
    lists 2026-2028; E.2 reads 2019-2025 from Wayback captures of the same page and logs any
    difference.
  - **EC-NFP and EC-FOMC.**
    - **Sources:** BLS Employment Situation release dates and the Federal Reserve's scheduled FOMC
      meetings, exactly as CatalogWriter-K2 fetched and specified them (reports/stage_e0_catalog_K2.md
      C9).
    - **Times:** 07:30 CT (Topstep F6 "Unemployment Rate | 7:30 AM", which lists 6A, 6B, 6C, 6E, 6J,
      6S, E7, M6A, M6E, 6N) and 13:00 CT (F6 "FOMC Statement | 1:00 PM | All products").
    - **Availability:** both schedules are published before the year or the release.
  - **EC-CAL.** The D10 FX calendar (trade dates, holidays, early halts and closes), built by E.2 from
    CME schedules.
  - **ME(m), month-end.** The last trade date of calendar month m in EC-CAL, known in advance.
    - **Month-end members** (K3-ldnrev-01, K3-mehedge-01) do not trade in month m if ME(m) is excluded
      by C4 or is an EC-EW bank holiday. Whether the WM/R month-end fix flow happens on a London holiday
      is not in the log. The drop removes 2020-08-31 and 2021-05-31 from the confirmation window and
      nothing from the research window (computed).
- **C10 Frequency (arithmetic from calendar counts, no price data).**
  - **Research window** 2025-04-01..2026-06-19:
    - 319 weekdays, about 305 CME trade dates;
    - 14 month-ends;
    - 298 Tokyo business days, 67 of them gotobi or Tokyo month-end days;
    - 314 weekdays that are not fixed TARGET holidays.
  - **Confirmation window** (the earliest S_X) 2019-05-06..2024-02-29:
    - 1,259 weekdays;
    - 58 month-ends, 56 after the EC-EW drop;
    - 1,179 Tokyo business days, 271 of them gotobi or month-end.
  - **All counts are before C4's exclusions.** A member trading on k of about 305 research dates, with
    zeros on the rest (D5), needs a net P&L per event of about (305 / k) x eps_X to average eps_X per
    trade date.
  - **The month-end members** (k about 14) need about 22 x eps_X per event. K3-tkypre-01 (k about 60)
    needs about 5 x.
  - **Likely verdicts:** the month-end members will probably be "inconclusive by design" or "null at
    eps" (D4's power check decides; the lead's 21:52 ruling Q4 keeps such members).
- **C11 Topstep items that do not bind in K3.**
  - **D9.11 volatility caps and D9.12 CPI window:** neither names any FX product (F12.1).
  - **D9.7 price-limit proximity:** no E.0 artifact establishes a CME daily price limit for FX futures.
    E.2's per-product limit tables decide, and if one exists, the harness rule applies. The catalog
    assumes nothing either way.
- **C12 Overnight coverage.**
  - **The problem:** D1(b) measured coverage only in 07:20-14:00 CT. Several members trade outside
    it: 6J at 17:30-01:00 CT, 6E from 00:46 CT.
  - **The check:** D9's member-level coverage check (>= 0.95 in the member's own window, research
    window) is therefore binding for them. E.2 computes it before screening.
  - **Supporting evidence, not a substitute for the check:** the log's only liquidity evidence for
    Asian hours is P-K3-006-a and b (21% of USD/JPY futures ADV and 12% of EUR/USD ADV trade in
    "(00:00 - 09:00a.m. GMT)"; over 180,000 G7 contracts a day in Asian hours).

---

## 1. Members

### K3-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K3. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures and admissible contracts** (each a separate trial): EUR {6E, E7, M6E*}; AUD
  {6A, M6A*}; GBP {6B, M6B}; CAD {6C}; JPY {6J}; CHF {6S}; NZD {6N}. Each is traded only if D2 admits
  the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log
  A10 and A28), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the trade
    date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the
    signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
    (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
  - **K3 log:** K3-010 (Seeck, London-open 30-minute momentum on spot FX and 6J) is this family on a
    K3 product and is recorded as **covered by CP1**. Its London-clock variant is not written (section
    5). D.1 A10 (Baltussen et al.) reappeared in the K3 search; its FX results are [unverified from
    K3's side].
- **Instantiated with the D6 FX row (O = 07:20, C = 14:00, F = 15:08):**
  - **Signal:** close of the bar at 07:49 minus the open of the trade date's first bar (the 17:00 CT
    bar of d-1, C3).
  - **Entry:** market intent on the bar at 13:29, filling at the 13:30 open.
  - **Exit:** market intent on the first bar at or after 13:58, filling nominally at the 13:59 open.
  - **Holding horizon:** 29 minutes. **Session window:** 13:30-13:59 CT. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid, with history
  2019-05..2026-06. The latest signal input, the 07:49 bar, is available at 07:50 CT; the decision is
  at 13:29.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (C6).
- **Parameters:** O+29 = 07:49, C-31 = 13:29, C-2 = 13:58 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes.
  Floor: at most 20 entries a day, ok; 2-minute minimum hold, ok; 10-minute mean hold, ok.
- **Falsification:** the standard condition only (a port). UCB95 of the member's mean net daily P&L
  per contract below eps_X, at >= 80% achieved null power on the confirmation window, counts against
  it.
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills.
  4. *: M6E (EUR) and M6A (AUD) are starred with the restriction unresolved. This applies only if D2
     picks them.
  5. News: 1 lot-equivalent, half the 2-lot maximum. On FOMC days the entry fills 30 minutes after the
     13:00 statement. That is exactly at the end of D8's 30-minute event-window cost; section 7, item 9.
  6. D9.5a: no fill in [07:30, 07:32) or [13:00, 13:02).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of each admitted K3 vehicle, research window 2025-04-01..2026-06-19 and
  confirmation S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K3-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K3. **Products read:** own vehicle.
- **Exposures:** EUR, AUD, GBP, CAD, JPY, CHF, NZD, one trial each, with the admissible contracts of
  K3-cp1-01. Each is traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py, hold_minutes =
  75), as fixed in D6 row CP2 with the 21:12 amendment and the 21:52 buffer ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market
    intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes
    after the fill, or the engine's forced flatten at F if earlier."
  - **D6 on the buffer:** "'4 ticks of P' in CP2 means 4 minimum price increments of the exposure's
    most active contract (D1 table), in price units, fixed whatever vehicle D2 chooses".
  - **K3 log:** it holds no opening-range source on FX futures.
- **Instantiated:**
  - **Opening range:** the bars opening in [07:20, 07:35).
  - **Eligible bars:** those opening in [07:35, 14:00). No entry from 14:00 CT on.
  - **Buffer, 4 ticks of the exposure's most active contract** (D1 table; ticks from C7):

    | Exposure | Most active | Buffer (price units) | In the other admissible contracts' ticks |
    |---|---|---|---|
    | EUR | 6E | 0.00020 | E7 2 ticks; M6E 2 ticks |
    | AUD | 6A | 0.00020 | M6A 2 ticks |
    | GBP | 6B | 0.0004 | M6B 4 ticks |
    | CAD | 6C | 0.00020 | none |
    | JPY | 6J | 0.0000020 | none |
    | CHF | 6S | 0.00020 | none |
    | NZD | 6N | 0.00020 | none |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is
    <= OR_low - buffer sells. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it (bars since entry), or the
    engine's forced flatten at F. An entry filled after 13:53 is cut short by F.
  - **Holding horizon:** 75 minutes or less. **Session window:** 07:36 to F.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known
  at 07:35 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks of the most active contract, hold 75 minutes (D6, a
  literal port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held up to 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: engine flatten at the latest.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. *: the M6E and M6A flag, as in CP1.
  5. News: 1 lot-equivalent.
     - On BLS days the opening range contains the 07:30 CT release (section 7, item 9).
     - Entries filled in 07:36-08:00 on those days pay D8's event-window cost.
  6. D9.5a: the earliest possible fill is 07:36, outside [07:30, 07:32).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K3-cp3-01 (core port CP3, prior-close location)
- **Cluster** K3. **Products read:** own vehicle.
- **Exposures:** EUR, AUD, GBP, CAD, JPY, CHF, NZD. Each is traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L over
    [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H.
    CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent
    on the O bar of day d. Exit: first bar at or after C-2 min."
- **Instantiated:**
  - **Daily bar:** O_d = open of the 07:20 bar. H and L are taken over the bars opening in
    [07:20, 14:00). C_d = close of the 13:59 bar.
  - **Complete day** (Family H): the 07:20 and 13:59 bars exist, the date is not an early halt, and
    every bar in [07:20, 14:00) carries one instrument_id.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of day d's 07:20 bar.
  - **CLV:** computed in ticks with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells (non-strict,
    as H6).
  - **Entry:** market intent on the 07:20 bar of d, filling at the 07:21 open.
  - **Exit:** first bar at or after 13:58, filling nominally at the 13:59 open.
  - **Holding horizon:** about 398 minutes. **Session window:** 07:21-13:59 CT.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar
  is complete at 14:00 CT on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 398 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: ok.
  4. *: the M6E and M6A flag.
  5. News: it holds through the 07:30 BLS release, the London fix and the 13:00 FOMC statement at
     1 lot-equivalent, which is not the full maximum (D9.5).
  6. D9.5a: the 07:21 entry is 9 minutes before the release; no fill in a guard window.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K3-ldnrev-01 (month-end London 4 p.m. fix: contrarian trade after the fixing window)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-05: the signal is the 10-minute pre-fix move, the close of the bar at T_L-1 minus the close of the bar at T_L-11, as NBER w23327 footnote 9 measures it ("the first-recorded price during 15:49:30 to 15:59:30" to "16:00:00"); the 15-minute window written below is superseded. The entry at T_L+5 stays as a stated judgment.]
- **Cluster** K3. **Products read:** the traded vehicle; EC-CAL, EC-EW; the T_L clock (C9).
- **Traded exposures:** EUR {6E, E7, M6E*}, JPY {6J}, CHF {6S}. Each is traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** rates that trend into the London 4 p.m. fix partly reverse after it, more at
    month-end: "the rates tend to drop after rising toward the fix, and tend to rise after dropping
    towards the fix. The larger reversal is found at the end-of-month trading days than intra-month
    days" (K3-002 P-K3-002-b).
  - **The trade is the source's own:** "taking a long (short) position after the end of fixing if the
    rates fell (rose) towards the fix" (P-K3-002-e); likewise "a simple end-of-month trading strategy
    of taking a long (short) position at 4:00 pm if prices fell (rose) towards the Fix" (K3-003
    P-K3-003-b).
  - **Post-reform evidence for this member's window:** "After the reform, the end-of-month
    profitability is still available ... While the profitability of holding one minute is no longer
    available, the profitability of 15 minutes holding becomes even stronger than before. In the
    intra-month sample, there are no profitability" (P-K3-002-f).
  - **Post-reform month-end cells, 15/5/1-minute holds, bp after spread** (P-K3-002-g):
    - EUR/USD "1.21 1.32 -1.02";
    - USD/JPY "2.39 2.27 -0.511";
    - USD/CHF "6.19 -0.0809 -1.45".
  - **Futures support:** futures positions built before the fix "are also reversed" (K3-018
    P-K3-018-a (6), CME 6B, 6A, 6N, pre-reform). The reversion is "two times larger on end-of-month"
    (K3-001 P-K3-001-c; the signs there are [unverified] in extraction, and this member's direction
    rests on the verbal statements of K3-002 and K3-003).
  - **Evidence against, stated both ways (rule 1):**
    - The regulator's data show the reversal gone after 2015 on all days pooled: "short-term price
      reversals in prices around the fix decrease steadily throughout our sample period, and disappear
      from 2015 onwards" (K3-019 P-K3-019-a; P-K3-019-b "from 2015 onwards the correlations are
      generally insignificant"). K3-019 pools all days by quarter and has a six-month post-reform
      sample. K3-002 splits out month-end and has about 16 post-reform months. So the two conflict on
      different day sets.
    - The pre-registered re-test on 2015-2023 (K3-020) is logged only as a protocol plus a Stage 2
      abstract, "the current 5-min window remains broadly effective" (P-K3-020-c). Its reversal
      result is [unverified].
    - For JPY, K3-003 (2004-2013) finds "the returns are positive for at least one horizon in all but
      the JPY/USD and USD/GBP" (P-K3-003-e), against K3-002's positive post-reform USD/JPY cell.
  - **Classification:** port of D.1 families C (short-horizon reversal) and E (month-end) on a fix
    event. D6 ports neither, so this is a cluster member (new to Stage E).
- **Exposure choice:** the three exposures whose post-reform month-end 15-minute cells are logged
  (P-K3-002-g). GBP is left out: K3-003 reports USD/GBP negative at every horizon, and K3-016's CME
  London trade on 6B is negative (P-K3-016-f). AUD and CAD are in K3-002's pair list, but their
  post-reform cells are not in the log (section 3).
- **Event set:** ME(m) for each month m, with C4 and the EC-EW drop (C9).
- **Signal:** M = close of the vehicle's bar at T_L - 1 minus close of its bar at T_L - 16. That is
  the move over the 15 minutes 15:45 to 16:00 London, bar closes. Both bars must exist with one
  instrument_id. M = 0 means no trade.
- **Entry rule:** market intent on the bar at T_L + 4, filling at the open of the bar at T_L + 5
  (16:05 London; 10:05 CT, or 11:05 CT in the C9 mismatch weeks). BUY if M < 0; SELL if M > 0.
  - This is contrarian in the futures' own quote, which is the source's rule for every pair: a
    reversal is unchanged by inverting the quote. For example, USD/JPY falling into the fix is 6J
    rising, and the source's long USD/JPY is a SELL of 6J.
- **Exit rule:** market intent on the bar at T_L + 19, filling at the open of T_L + 20 (10:20 CT
  standard).
- **Holding horizon:** 15 minutes. **Session window:** 10:05-10:20 CT (11:05-11:20 in the mismatch
  weeks). Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close, open and instrument_id (C8). Paid, 2019-05..2026-06. The signal is
    available at T_L (the close of the bar at T_L - 1), 5 minutes before the entry fill.
  - EC-CAL and EC-EW. Free, 2019-2026, known in advance (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Pre-fix window, 15 minutes:** a judgment. The log does not give K3-002's window length. The
    choice follows the 15-minute pre-fix windows of the post-reform efficiency tests ("the 15 minutes
    before the fix", P-K3-019-b and P-K3-020-a) and the 15:45 start of the post-reform fix trend
    (P-K3-017-b).
  - **Entry at T_L + 5:** a judgment. After the reform "the fixing time window was widened from 1
    minute to 5 minutes" (P-K3-002-d), and the log does not say how the window is centred. An entry at
    16:05 London is after that window under either centring, and K3-002 trades "after the end of
    fixing".
  - **Hold 15 minutes:** P-K3-002-f and P-K3-002-g.
  - **Grid:** none.
- **Expected entries and hold:** one per eligible month-end: about 14 in the research window and 56
  in the confirmation window, before C4. Held 15 minutes. Floor ok: the 2-minute minimum and the
  10-minute mean both hold. Frequency: C10, about 22 x eps_X per event.
- **Falsification:**
  - The standard condition (UCB95 of mean net daily P&L per contract below eps_X at >= 80% achieved
    null power on the confirmation window counts against it).
  - **Sign check (reported beside the verdict, not a separate test):** the mean over events of
    direction x (open at T_L + 20 - open at T_L + 5), in ticks, is positive. A non-positive
    confirmation-window mean counts against the mechanism.
- **Topstep check:**
  1. Flat by F: latest fill 11:20 CT.
  2. Order type: market.
  3. D9.4: one trade a month.
     - Both fills are outside the fix minute and the post-reform fixing window.
     - The fix minute is the day's peak-volume minute, "over 10% of the platform's daily trading
       volume" on some days (P-K3-013-d), not a gapped market.
  4. *: M6E flag (EUR only, if D2 picks M6E).
  5. News: 1 lot-equivalent. No Topstep-listed release falls in the window.
  6. D9.5a: not triggered (no fill at 07:30 or 13:00).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the EUR, JPY and CHF vehicles (research and confirmation windows);
  external EC-CAL and EC-EW.
- **Trials in N:** 1 per admitted exposure (at most 3).

### K3-ldnmom-01 (post-reform front-running into the London 4 p.m. fix)
- **Cluster** K3. **Products read:** the traded vehicle; EC-CAL, EC-EW; the T_L clock.
- **Traded exposures:** EUR {6E, E7, M6E*}, JPY {6J}. [Narrowed by the lead, 01:40 PDT 2026-09-24, answering
  this writer's question 3: the mechanism rests on a flow model with no profitability test, so the trial
  count is cut from 6 to 2, keeping the two most liquid K3 exposures by 2026 Jan-Aug ADV (D1 table). GBP, CHF,
  CAD and NZD are removed; the rest of the entry is unchanged.]
  Each is traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** after the 2015 reforms, fix dealers execute client fix orders with algorithms
    from about 3:45 p.m. London. So "non-dealers can now glean information about fix orders from the
    price trend immediately following 3:45 ... front-run the rest of the market by opening a
    speculative position immediately after 3:45 and then liquidate that position partly before and
    partly after the fix" (K3-017 P-K3-017-b).
  - **The model:** "Fix prices will be unusually volatile without collusion ... dealers front-run each
    other" (P-K3-017-a).
  - **Supporting descriptive evidence:** the pre-fix trend is visible in the average price path
    (P-K3-002-b, "rising toward the fix"). The minute before the fix "shows a significant increase in
    volatility compared to the minutes in the ~50-min. beforehand" (K3-021 P-K3-021-a). The fix raises
    the probability of the day's extreme (P-K3-021-c).
  - **Evidence against, stated:**
    - The source tests the convexity of the pre-fix path, not profitability. Its post-reform claim
      rests on other papers (the K3-017 block, "Quality tells").
    - After 2015 "dealer banks began doing relatively less trading before the fix and more during the
      fix" (P-K3-019-a), which weakens pre-fix pressure.
    - The Norges Bank study found no significant price changes around the WM fix in its currencies
      (K3-004 P-K3-004-d).
    - Futures positions built before the fix reverse afterwards (P-K3-018-a (6)). That works against
      the post-fix part of this member's hold.
  - **Classification:** port of D.1 family C (short-horizon momentum) at the fix clock. D6 does not
    port it, so it is a cluster member (new to Stage E).
- **Exposure choice:** the source's currencies that are K3 exposures, "EUR, JPY, GBP, CHF, CAD, NZD,
  and DKK" (P-K3-017-c). AUD is not in the source's sample.
- **Event set:** every trade date d with C4, excluding EC-EW bank holidays (C9: whether a London fix
  flow exists on a London holiday is not in the log).
- **Signal:** S = close of the vehicle's bar at T_L - 13 minus open of its bar at T_L - 15. That is the
  trend over the three bars opening 15:45, 15:46 and 15:47 London, "immediately following 3:45". Both
  bars must exist with one instrument_id. S = 0 means no trade.
- **Entry rule:** market intent on the bar at T_L - 13, filling at the open of the bar at T_L - 12
  (15:48 London; 09:48 CT standard). BUY if S > 0; SELL if S < 0.
- **Exit rule:** market intent on the bar at T_L + 4, filling at the open of the bar at T_L + 5 (16:05
  London; 10:05 CT standard).
- **Holding horizon:** 17 minutes. **Session window:** 09:48-10:05 CT (10:48-11:05 in the mismatch
  weeks). Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). The signal is available
  at T_L - 12. EC-CAL and EC-EW (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Signal window of 3 minutes starting at 15:45:** a judgment. The source says only "immediately
    following 3:45". Three bars is the shortest window that measures a trend rather than one bar's
    noise, while still leaving most of the run-up to the fix to be traded.
  - **Exit at T_L + 5:** a judgment within "partly before and partly after the fix". A single-lot
    position cannot be split, so it is held through the fix to the end of the post-reform fixing
    window under either centring (P-K3-002-d).
  - **Why not exit before the fix:** an exit before the fix (at T_L - 3) would make the hold 9
    minutes, below D9.3(c)'s 10-minute mean.
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date (about 290 research dates after C4 and the
  12 EC-EW weekday holidays), held 17 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of direction x (open at T_L - 3 - open at T_L - 12), in
    ticks, is positive. That is the pre-fix part, which the mechanism predicts. The post-fix part is
    reported beside it.
- **Topstep check:**
  1. Flat by F: latest fill 11:05 CT.
  2. Order type: market.
  3. D9.4: one trade a day, held 17 minutes. No fill in the fix minute (16:00-16:01 London).
  4. *: M6E flag (EUR).
  5. News: 1 lot-equivalent. No Topstep-listed release falls in the window.
  6. D9.5a: not triggered.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the six vehicles (research and confirmation windows); external EC-CAL
  and EC-EW.
- **Trials in N:** 1 per admitted exposure (at most 2, after the lead's narrowing).

### K3-mehedge-01 (month-end equity-hedge rebalancing in the hour before the London fix)
- **Cluster** K3. **Products read:** the traded vehicle; one non-CME equity index per exposure (a
  signal instrument, which belongs to the traded product's cluster: partition section 1 and the
  lead's 21:52 ruling, "Melvin-Prins stays in K3"); EC-CAL, EC-EW; the T_L clock.
- **Traded exposures:** EUR {6E, E7, M6E*} with the EURO STOXX 50 price index; JPY {6J} with the
  Nikkei 225. Each is traded only if D2 admits the exposure **and** E.2 obtains the index's free daily
  history (below). **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** international equity managers resize their currency hedges at the month-end
    London fix. Where the local equity market has risen over the month, foreign holders own more of
    that currency and sell it into the fix. "Equity market appreciation over the month predicts
    currency depreciation before the end-of-month fix" (K3-001 P-K3-001-a).
  - **Magnitude:** "a 10% equity appreciation leads to 14 basis points of currency depreciation. Though
    significant, this seems like quite a small effect" (P-K3-001-b).
  - **Flows:** month-end flows are 1.39 to 2.36 times non-month-end flows, "significantly greater than
    1" in every country (P-K3-001-e). Month-end fix flow can reach CME FX futures through FX BTIC
    (R-K3-014, verbatim in the log).
  - **Sample:** 2004-2012 (P-K3-001-d). The authors are BlackRock practitioners. The regression R2 is
    low (the K3-001 block).
  - **Classification:** new to the program (the partition's K3 seed); a port of D.1 family E (month
    end) with an external signal.
- **Exposure choice (rule 3):**
  - **The source's signal:** "Datastream Total Market indices" (the K3-001 block), which are
    proprietary.
  - **The obtainable proxy:** each currency area's benchmark price index, in local currency, from its
    publisher. Only EUR and JPY have a named publisher history candidate:
    - STOXX Ltd.'s daily history file for the EURO STOXX 50 (h_3msx5e.txt);
    - Nikkei Inc.'s Nikkei 225, which FRED also redistributes as series NIKKEI225.
  - **Not confirmed:** neither was confirmed from this machine (header: certificate error, a Wayback
    capture exists; FRED unreachable; Nikkei 403).
  - **Other exposures:** GBP, AUD, CAD, CHF and NZD are in the source's sample, but no free historical
    source was named for their indices. They are excluded under rule 3 (section 2, X-13).
  - **Judgment on the index:** the broad Datastream index is replaced by the publisher's blue-chip
    index. This is a judgment: the blue-chip index is what the publisher releases free.
- **Event set:** ME(m) with C4 and the EC-EW drop (C9).
- **Signal:**
  - **Formula:** R_eq(m) = ln(P_a / P_b), where P_a is the index's last official daily close on a local
    date strictly before ME(m)'s calendar date, and P_b is its last official daily close in calendar
    month m-1.
  - **Timing:** in the normal case P_a is the close of the local second-last trading day, matching the
    source's "equity return over the month up to the second-last day" (K3-001 block). The Tokyo close
    on ME's own date label is excluded even though it precedes the entry, to match the source.
  - **No trade** if R_eq(m) = 0 or either close is missing.
- **Entry rule:** market intent on the bar at T_L - 61, filling at the open of the bar at T_L - 60
  (15:00 London; 09:00 CT standard). SELL if R_eq(m) > 0 (the currency is predicted to depreciate);
  BUY if R_eq(m) < 0.
- **Exit rule:** market intent on the bar at T_L - 4, filling at the open of the bar at T_L - 3 (15:57
  London; 09:57 CT standard).
- **Holding horizon:** 57 minutes. **Session window:** 09:00-09:57 CT (10:00-10:57 in the mismatch
  weeks). Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open and instrument_id (C8).
  - EURO STOXX 50 official daily close: source STOXX Ltd. history file. Free per the publisher's
    listing, but its 2019-04..2026-06 availability is **[unverified in E.0]**. Available at the index's
    official close on each date (STOXX closes during European hours, before 12:00 CT), at least 20
    hours before the entry.
  - Nikkei 225 official daily close: source Nikkei Inc. or FRED NIKKEI225. Free, availability
    **[unverified in E.0]**. Available at the Tokyo close on each Tokyo date, before 02:00 CT on the
    same date label, at least one day before the entry.
  - EC-CAL and EC-EW (C9).
  - **E.2 rule:** if an index's free daily history from 2019-04 cannot be obtained before any K3 bar is
    read, that exposure's trial is dropped and logged, never substituted.
- **Order type:** market. **Sizing:** q_c. The source's effect is linear in R_eq, but D2 forbids
  signal-scaled size above q_c, so the size is fixed.
- **Parameters:**
  - **Window, the hour before the fix:** the source says "in the hour leading up to the end of month
    fix" (P-K3-001-b).
  - **How "15:00-16:00 GMT" is read:** as London clock time. The passage defines the window as the
    hour before the 4 p.m. London fix, and a literal UTC reading would put it after the fix in British
    Summer Time months.
  - **Exit 3 minutes early:** a judgment, so that the position is flat before the post-reform 5-minute
    fixing window under either centring (P-K3-002-d).
  - **Grid:** none.
- **Expected entries and hold:** about 14 research and 56 confirmation events (C10), held 57 minutes.
  Floor ok. About 22 x eps_X per event is needed (C10).
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the correlation between R_eq(m) and the vehicle's move from the
    T_L - 60 open to the T_L - 3 open is negative.
- **Topstep check:**
  1. Flat by F: latest fill 10:57 CT.
  2. Order type: market.
  3. D9.4: one trade a month, no stops.
  4. *: M6E flag (EUR).
  5. News: 1 lot-equivalent. The window can contain a 09:00 CT US release that is not in Topstep's
     table, which is allowed at this size.
  6. D9.5a: not triggered.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the EUR and JPY vehicles; external index closes from 2019-04 (the
  confirmation window's first month needs April 2019's last close); EC-CAL and EC-EW.
- **Trials in N:** 1 per admitted exposure with an obtained index (at most 2).

### K3-ecbfix-01 (euro: dollar strength into the ECB fix, dollar weakness after it)
- **Cluster** K3. **Products read:** the EUR vehicle; EC-CAL, EC-TGT; the T_E clock.
- **Traded exposure:** EUR {6E, E7, M6E*}, traded only if D2 admits the exposure. **Vehicle:** D2
  (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** dealers meet an unconditional demand for dollars at the major fixes, so
    "intraday currency returns display prolonged reversals around the major benchmark fixings,
    characterised by an appreciation of the U.S. dollar pre-fixing and a depreciation thereafter",
    present "every day of the week, month of the year, and during each of the twenty years" (K3-016
    P-K3-016-a).
  - **The source's trade:** "For the ECB fix we go long the dollar between 2:00 a.m. and 8:15 a.m. and
    short the U.S. dollar between 8:15 a.m. and 5:00 p.m." (ET; P-K3-016-d).
  - **On CME futures with full bid-ask costs, 2009-2018:** "returns for trading the euro are extremely
    large and generate a Sharpe ratio for the ECB fix trade of 0.61" (P-K3-016-e).
  - **Table 8 CME row** (P-K3-016-f): pre-E 5.53% a year (Sharpe 0.99), post-E 0.58% (0.08), pre/post-E
    6.11% (0.65). The text's 0.61 and the table's 0.65 disagree; the log records it.
  - **Corroboration, the same direction in overlapping hours:**
    - Breedon and Ranaldo: currencies "depreciate during local trading hours". For EUR/USD the
      strategy survives costs, "Sharpe Ratios of 1.3 and 0.9 respectively for the morning short and
      afternoon long" (K3-023 P-K3-023-a, b). The between-session difference is stable year to year
      (P-K3-023-c).
    - Ranaldo: "long position on US dollars is from 8:00 to noon" against the euro, short "from 16:00
      to 20:00 for the euro" (GMT; K3-024 P-K3-024-d). The EUR/USD break-even cost is 4 pips
      (P-K3-024-c).
    - On IMM futures (pit era, abstract only), foreign currencies strengthen during the US day
      (K3-025 P-K3-025-a).
    - Activity rises ahead of the ECB fix (K3-004 P-K3-004-b).
  - **Against:** with full spread costs most spot windows turn negative, and the authors say "it is
    not obvious that this can be exploited by the average trader" (P-K3-016-g, h). Only the CME euro
    cell is positive.
  - **Classification:** new to the program; a port of D.1 family A (session clock) anchored to a fix.
    D6 does not port family A because a clock drift needs a documented drift on the product. This one
    is documented on 6E itself.
- **Exposure choice:** EUR only. It is the only exposure the source's CME test supports ("returns and
  Sharpe ratios are negative for the pound and the yen", P-K3-016-e), and the only pair that survives
  costs in K3-023 (P-K3-023-b).
- **Event set:** every trade date d with C4 that is not an EC-TGT closing day (no ECB fix: "except on
  TARGET closing days", ECB page, header).
- **Entry and exit rules (two legs, sequential, at most one position):**
  - **Leg 1 (pre-fix, SELL):** market intent on the bar at 00:59 CT, filling at the 01:00 CT open.
    The source's 2:00 a.m. ET is 01:00 CT all year, because ET and CT change clocks together. Exit:
    market intent on the bar at T_E - 1, filling at the T_E open (07:15 CT, or 08:15 CT in the C9
    mismatch weeks).
  - **Leg 2 (post-fix, BUY):** market intent on the bar at T_E, filling at the T_E + 1 open. Exit:
    market intent on the bar at 15:04 CT, filling at the 15:05 open. The source's 5:00 p.m. ET = 16:00
    CT is later than F, so the leg is truncated to 15:05 (as the K3-016 block notes).
- **Holding horizon:** leg 1 375 minutes (435 in the mismatch weeks); leg 2 469 minutes (409).
  **Session window:** 01:00-15:05 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL and EC-TGT (known in
  advance).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Leg 1:** 01:00 CT to T_E (P-K3-016-d). **Leg 2:** T_E to 15:05 CT (P-K3-016-d, truncated by F).
  - **The one-minute gap at the fix:** a judgment. The reversal is written as exit then re-entry, so
    the position never exceeds q_c.
  - **Grid:** none.
- **Expected entries and hold:** 2 entries per eligible trade date (about 300 research dates before
  C4), each held hours. Floor ok: 2 <= 20 entries a day, and every hold exceeds 10 minutes.
- **Falsification:**
  - The standard condition.
  - **Sign checks (reported per leg):** leg 1's mean gross move, SELL-signed, is positive, and so is
    leg 2's, BUY-signed. The source predicts both. A leg with a non-positive confirmation mean counts
    against that leg's half of the mechanism.
- **Topstep check:**
  1. Flat by F: last fill 15:05.
  2. Order type: market.
  3. D9.4: two trades a day, no stops. The 01:00 entry is not at a session reopen.
  4. *: M6E flag.
  5. News: leg 2 holds through the 07:30 BLS release (or leg 1 does, in the mismatch weeks) and the
     13:00 FOMC statement at 1 lot-equivalent (F6.3, D9.5).
  6. D9.5a: no fill in [07:30, 07:32) or [13:00, 13:02). The leg-2 fill at 08:16 in a mismatch week
     is 46 minutes after 07:30, outside D8's 30-minute event-window cost.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the EUR vehicle 01:00-15:05 CT (research and confirmation windows; the
  C12 coverage check applies to 01:00-07:20); external EC-CAL and EC-TGT.
- **Trials in N:** 1.

### K3-tkypre-01 (gotobi days: dollar demand into the Tokyo 9:55 fix)
- **Cluster** K3. **Products read:** the JPY vehicle; EC-CAL, EC-JP; the T_T clock.
- **Traded exposure:** JPY {6J}, traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2; 6J is the only admissible contract).
- **Mechanism:**
  - **What is claimed:** at the Tokyo fix, importers' dollar purchases exceed exporters' sales,
    predictably. "It is commonly known that the USD tends to appreciate vis-à-vis the yen around the
    fixing time. This situation is more evident when large amounts of payments are due, typically on
    the days of the 5th, 10th, 15th, 20th, 25th, and 30th ... as well as the end-of-month trading day"
    (K3-022 P-K3-022-b).
  - **Calendar strength:** "the return becomes particularly high at 5th and 10th days (except for the
    days close to the end of month), and the 31st day of month or the end of month" (P-K3-022-d).
  - **Morning path:** "the USD/JPY rate tends to rise toward 9:55 every morning in the Gotobi days"
    (K3-005 P-K3-005-a).
  - **K3-005's pre-fix leg** (long USD/JPY, 3:00 to 9:55 JST, 2018-2020): profit factor 1.46 on gotobi
    days against 0.51 on other days, without the moving-average filter (P-K3-005-c).
  - **Against:**
    - K3-005 is a 4-page paper with three in-sample years, and an author works at an FX broker (the
      K3-005 block).
    - K3-022's own trade earns 1.8 bp, "slightly above the transaction cost from the bid-ask spread"
      (P-K3-022-c).
    - K3-016's unconditional (every-day) pre-Tokyo long-dollar trade on CME 6J loses after full
      spread, "-11.23" % a year (P-K3-016-f). That is evidence against the all-days version; the
      gotobi-conditioned version is not tested there.
  - **Classification:** new to the program; a port of D.1 families A (clock) and E (calendar).
- **Event set:** trade dates d such that d, as a Tokyo date, is an EC-JP Tokyo business day whose day
  of month is 5, 10, 15, 20, 25 or 30, or the last EC-JP business day of its calendar month. C4
  applies.
  - **No shift rule:** a nominal gotobi date that is not a Tokyo business day is not moved to another
    day. The log states no shift rule (P-K3-005-a: "divisible by five"), so only nominal dates are
    traded; this is a judgment.
- **Entry rule:** SELL (a rise in USD/JPY is a fall in 6J, C8). Market intent on the bar at 17:29 CT
  on calendar day d-1, filling at the 17:30 CT open, which is 08:30 JST under CST and 07:30 JST under
  CDT.
- **Exit rule:** market intent on the bar at T_T - 1, filling at the open of the bar at T_T (09:55:00
  JST: 18:55 CST or 19:55 CDT on d-1). That is the source's exit time: K3-005 exits at 9:55, and
  K3-022 switches "at the moment of the Tokyo fixing".
- **Holding horizon:** 85 minutes (CST) or 145 minutes (CDT). **Session window:** 17:30-19:55 CT on
  d-1, inside trade date d (C3). Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL and EC-JP (C9; known years
  ahead).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Gotobi set:** P-K3-022-b and P-K3-022-d.
  - **Exit at T_T:** P-K3-005-b and P-K3-022-c.
  - **Entry at 17:30 CT:** the source's 3:00 JST entry (P-K3-005 block) is 18:00 UTC, which is 12:00
    CST or 13:00 CDT on calendar day d-1. That falls in trade date d-1's day session, so the position
    would be held across Topstep's 15:10 CT close; it is infeasible (partition rule 8).
    - The earliest feasible entry is the 17:00 CT reopen. Thirty minutes are added so that the entry
      is not a fill at the session reopen, the D9.4 "gapped markets" case.
    - This is a judgment: the log does not locate the drift within the morning.
  - **Grid:** none.
- **Expected entries and hold:** about 67 research and 271 confirmation gotobi or month-end Tokyo
  business days, before C4 and CME closures (C10). Held 85 or 145 minutes. Floor ok. About 5 x eps_X
  per event is needed (C10).
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean gross move of 6J from the 17:30 open to the T_T open on event
    days is negative.
  - **Reported beside it:** the same statistic on non-gotobi Tokyo business days. The mechanism
    predicts it is closer to zero (P-K3-005-c's gotobi/non-gotobi contrast).
- **Topstep check:**
  1. Flat by F: latest fill 19:55 CT on d-1.
  2. Order type: market.
  3. D9.4: one trade per event, entered 30 minutes after the reopen, not in a gap. The exit is at the
     fix minute's open, and the fix is a scheduled benchmark, not a release.
  4. *: none (6J is unstarred).
  5. News: 1 lot-equivalent; no Topstep-listed release at 17:30-19:55 CT.
  6. D9.5a: not triggered.
  7. Position limit: 1 contract.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the JPY vehicle in 17:00-20:00 CT (research and confirmation windows;
  the C12 coverage check applies); external EC-CAL and EC-JP.
- **Trials in N:** 1.

### K3-tkypost-01 (dollar weakness after the Tokyo fix, every Tokyo business day)
- **Cluster** K3. **Products read:** the JPY vehicle; EC-CAL, EC-JP; the T_T clock.
- **Traded exposure:** JPY {6J}, traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:**
  - **What is claimed:** after the Tokyo fix the dollar depreciates: "Immediately after the Tokyo fix
    the price path of the DOL reverses, depreciating by ~5.5% per annum (2.2 bps per day) with a
    t-statistic of ~9.2" (K3-016 P-K3-016-b, spot dollar factor).
  - **The source's window:** "short dollar positions between 8:55 p.m. and 2:00 a.m." (ET;
    P-K3-016-d).
  - **On CME 6J with full spread, 2009-2018:** the post-Tokyo leg earns 2.41% a year, Sharpe 0.52.
    It is the only positive Tokyo cell; pre-T is -11.23 and pre/post-T -8.82 (P-K3-016-f).
  - **Corroboration:** K3-005's second leg sells USD/JPY "just after 9:55 and closing its position at
    12:00" (P-K3-005-b). Its profit factor 2.09 is conditional on an ex-post classification (a
    look-ahead flag; see X-02), so it is not used as evidence of size.
  - **Against:** K3-022 finds the London-style reversal absent at Tokyo: "While return reversals are
    reported at the London fixing ..., they are not found at the Tokyo fixing (Table 4)" (P-K3-022-c).
    That test is a reversal correlation, whereas this member is an unconditional post-fix drift, but
    the two findings pull in opposite directions.
  - **Classification:** new to the program; a port of D.1 family A anchored to a fix.
- **Event set:** every trade date d such that d, as a Tokyo date, is an EC-JP Tokyo business day. C4
  applies.
- **Entry rule:** BUY (dollar weakness is a rise in 6J). Market intent on the bar at T_T, filling at
  the open of the bar at T_T + 1 (09:56 JST: 18:56 CST or 19:56 CDT on d-1).
- **Exit rule:** market intent on the bar at 00:59 CT on d, filling at the 01:00 CT open. The source's
  2:00 a.m. ET is 01:00 CT all year.
- **Holding horizon:** 364 minutes (CST) or 304 minutes (CDT). **Session window:** 18:56 on d-1 to
  01:00 CT on d, inside trade date d. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL, EC-JP.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Start after the fix minute; end at 01:00 CT:** P-K3-016-d.
  - **Anchoring:** the source's windows are stated in ET for the daylight-time case ("8:55 p.m. ET (or
    7:55 p.m. depending on ... DST)", P-K3-016-c). This member anchors the start to the actual fix on
    every date (C9), a judgment in line with the fix mechanism.
  - **Grid:** none.
- **Expected entries and hold:** about 298 research and 1,179 confirmation Tokyo business days before
  C4 and CME closures, held 5-6 hours. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean gross move of 6J from the T_T + 1 open to the 01:00 open is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 01:00 CT.
  2. Order type: market.
  3. D9.4: one trade a day; entered one minute after the fix minute, not at a reopen.
  4. *: none.
  5. News: 1 lot-equivalent. Asian-hours releases are not in Topstep's table.
  6. D9.5a: not triggered.
  7. Position limit: 1 contract.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the JPY vehicle 18:55-01:00 CT (research and confirmation windows; the
  C12 coverage check applies); external EC-CAL, EC-JP.
- **Trials in N:** 1.

### K3-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 ADV order): EUR, JPY, AUD, GBP, CAD, NZD, CHF; if none is admitted, no ML member. Features unchanged.]
- **Traded vehicle: the EUR exposure** {6E, E7, M6E*}; the contract is chosen by D2 in E.2.
  - **Reason:** EUR is the K3 exposure the log supports most, and the most tested on CME futures:
    - the only positive CME fix trade (K3-016 P-K3-016-e, f);
    - the only time-of-day strategy that survives costs (K3-023 P-K3-023-b; K3-024 P-K3-024-c);
    - a post-reform month-end fix cell (K3-002 P-K3-002-g);
    - price discovery and volatility studies on the euro future (K3-026, K3-027, K3-029, K3-030,
      K3-033).
  - **Liquidity:** EUR also has the cluster's highest public ADV, 6E 216,466 contracts a day in 2026
    Jan-Aug (D1 table).
  - **No fallback is declared.** The features below are EUR- and fix-specific. If D2 admits no EUR
    contract, the lead decides.
  - **Star flag:** if D2 picks M6E, the unresolved * restriction applies (D9.8).
- **Products the features read:**
  - The EUR vehicle.
  - The vehicles of the other admitted K3 exposures (JPY, GBP, AUD, CAD, CHF, NZD), for KF5 only.
  - Calendars: EC-CAL, EC-NFP, EC-FOMC, and the T_E and T_L clocks (C9).
- **Cluster features (7; with D15.4's B1-B5, 12).** Notation:
  - t_j is the decision time, and the last bar closed at t_j is the bar at t_j - 1.
  - "tick" is the vehicle's tick.
  - A missing bar, or a change of instrument_id inside a feature's bars, means no trade at t_j.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | fix_phase | 0 if t_j < T_E(d); 1 if T_E(d) <= t_j < T_L(d); 2 if t_j >= T_L(d). The clocks are from C9, on every date (a clock-only feature) | K3-016 P-K3-016-a (dollar up before each fix, down after), P-K3-016-c (fix times), P-K3-016-d (windows) | calendar and clock, known before d |
| KF2 | month_end | 1 if d = ME(m) (C9), else 0 | K3-001 P-K3-001-a, P-K3-001-e; K3-002 P-K3-002-b, P-K3-002-f; K3-003 P-K3-003-b | EC-CAL, known in advance |
| KF3 | ldn_prefix_ret | If t_j >= T_L(d): (close of the bar at T_L - 1 - open of the bar at T_L - 60) / tick, the London 15:00-16:00 hour; else 0 | K3-001 P-K3-001-c (the 15:00-16:00 return predicts reversion from 16:00, "on all days", "two times larger on end-of-month"; signs [unverified] in extraction, so the model learns the sign) | T_L (close of the bar at T_L - 1) <= t_j |
| KF4 | heat_wave_rv | Mean of abs(close - open) / tick over the vehicle's bars whose CT open time lies in [t_j, t_j + 60) on the most recent earlier trade date in EC-CAL that is not an early halt. At least 30 of those 60 bars are required, else no trade at t_j | K3-033 P-K3-033-a ("the economic significance of own-region spillovers is much more important than that of inter-region spillovers"); K3-030 P-K3-030-a ("intraregion volatility (heat waves)") | the previous trade date's bars, closed before d begins |
| KF5 | dol_ret60 | -(10,000 / n) x sum over X in S of (close of X's vehicle bar at t_j - 1 - open of X's bar at t_j - 60) / open of X's bar at t_j - 60. S is the set of admitted K3 exposures other than EUR, frozen in E.2 before any fit; n is the number of X in S with both bars on one instrument_id; n >= 4 required, else no trade at t_j. The sign makes a positive value a dollar appreciation (every K3 contract is quoted in USD per foreign unit, P-K3-007-b) | K3-016 P-K3-016-a, P-K3-016-b (the dollar factor "DOL" carries the fix pattern) | bars closed <= t_j |
| KF6 | nfp_phase | If d is an EC-NFP release date: -1 if t_j < 07:30 CT, +1 if t_j >= 07:30 CT; else 0 | K3-032 P-K3-032-b (a jump within minutes, no drift after), P-K3-032-c (volume 18 to 22 times average); K2-015 P-K2-015-a [K3] ("news produces conditional mean jumps"); K3-029 P-K3-029-a (nonfarm payroll surprises move FX futures) | calendar known in advance |
| KF7 | fomc_phase | If d is an EC-FOMC statement date: -1 if t_j < 13:00 CT, +1 if t_j >= 13:00 CT; else 0 | K3-009 P-K3-009-a (intraday currency futures react to FOMC surprises, "the reaction is short-lived", asymmetric) | calendar known in advance |

- **Decision window [W0, W1] = [00:45, 13:45] CT; horizon h = 60 minutes.**
  - **Decision times:** t_j = 00:45, 01:45, ..., 13:45, which is 14 a day. W1 + h = 14:45 <= F.
  - **Fills:** by D15.3's convention a position runs from the open of t_j + 1 to the open of t_j + 60,
    so every fill falls at :46 or :45.
  - **Why this window:**
    - It opens with the European morning, where K3-016's pre-ECB leg starts (01:00 CT, P-K3-016-d)
      and K3-024's European block lies (P-K3-024-d).
    - It ends inside the day session, before C.
    - The :45 offset puts every scheduled K3 event minute strictly inside a position interval, never
      at a fill:
      - the ECB fix at 07:15 or 08:15;
      - the 07:30 BLS release;
      - the 10:00 ET (09:00 CT) option expiry (P-K3-032-a, P-K3-021-b);
      - the London fix at 10:00 or 11:00;
      - the 13:00 FOMC statement;
      - the 14:00 settlement.
  - **Why h = 60:**
    - The logged EUR effects play out over hours (K3-016's multi-hour fix windows; K3-024's 4-hour
      blocks), and K3-001's pre-fix effect is one hour (P-K3-001-b).
    - h = 15 or 30 would sit inside the release jumps, which show no drift afterwards (P-K3-032-b).
      It would also need 20 or more decisions a day to cover the European morning.
    - h = 120 would fold the ECB fix, the 07:30 release and the London fix into one or two intervals.
- **Expected rows:** 14 per eligible research-window trade date: about 305 trade dates, less roll
  blackout, vendor-degraded and early-halt dates (D15.3), and less the 20-date warm-up of B4. That is
  roughly 3,400-4,000 rows; E.2 gives the exact count. B3 (minutes since O = 07:20) is negative before
  07:20, by definition.
- **Expected entries:** at most 14 per day (<= 20), each held 60 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it). Failing the D5 screen puts
  it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 14:45.
  2. Order type: market (D15.6).
  3. D9.4: at most 14 entries a day, 60-minute holds, no stops or brackets. No fill in a release or
     fix minute.
  4. *: M6E flag.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span a release. On BLS days
     the 07:45 and 07:46 fills pay D8's event-window cost.
  6. D9.5a: no fill in [07:30, 07:32) or [13:00, 13:02) by construction.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:**
  - ohlcv-1m of the EUR vehicle and of every vehicle in S. The research window is used for training
    and tuning, the confirmation window for the frozen model.
  - The member-level coverage check covers 00:46-14:45 for the EUR vehicle (C12).
  - External: EC-CAL, EC-NFP, EC-FOMC.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K3-tkyswitch-01 | 6J short 5 minutes before and long 5 minutes after the Tokyo fix, the source's "holding the USD/JPY long for five minutes and then shorting it for the following five minutes" (K3-022 P-K3-022-c) | D9.3 floor; D9.4 | Five-minute holds give a mean hold of 5 minutes, below D9.3(c)'s 10-minute floor. Both fills sit at the fix minute. The edge, 1.8 bp, is "slightly above the transaction cost from the bid-ask spread" (P-K3-022-c), which the futures spread plus commission would consume. The longer-window versions are K3-tkypre-01 and K3-tkypost-01 |
| X-02 K3-gotrev-01 | 6J BUY from just after 9:55 to 12:00 JST on gotobi days only (K3-005 P-K3-005-b) | Rule 14 (look-ahead in the only evidence) | Its only logged figure, profit factor 2.09, is "In the days when the Gotobi anomaly occurred" (P-K3-005-d): conditional on an ex-post classification. No unconditional gotobi-day figure is logged. The all-days post-fix drift, tested on CME 6J, is K3-tkypost-01 |
| X-03 K3-tkypre-src-01 | K3-tkypre-01 with the source's 3:00 JST entry, or its golden-cross entry between 2:30 and 3:00 JST (K3-005 block) | Flat by F (partition rule 8) | 3:00 JST falls at 12:00 CST or 13:00 CDT of the previous trade date, so the position would be held across Topstep's 15:10 CT close. Written truncated as K3-tkypre-01. The golden-cross filter's window "n = 3" was chosen in sample as "the best" (the K3-005 block) and is not ported |
| X-04 K3-chnpmi-01 | 6A, 6N, 6C (and 6J, opposite sign) traded on Chinese PMI surprises: "Australian dollar 35 0.12 (0.03)*** ... Japanese Yen 35 -0.04" per one-SD surprise (K3-007 P-K3-007-d, e) | Rule 3; rule 1 | The surprise needs the consensus forecast, a proprietary survey with no named obtainable history. With the price response as a proxy nothing is left to trade: the move is complete inside the "10 minutes before to 10 minutes after" window (P-K3-007-c) and "appears to be permanent" (first-run passage, not re-checked). The pre-announcement CARs are "available upon request" and not shown (P-K3-007-g), so no direction or window can be traced. The release is also at US night, when D1 coverage was not measured |
| X-05 K3-usrel-01 | 6E or 6J traded on US macro release surprises (NFP and others) (K3-032 P-K3-032-a, b; K2-015 P-K2-015-a [K3]; K3-029 P-K3-029-a; K3-031 title only) | Rule 3; D9.5a; D9.4; evidence | The surprise needs the proprietary consensus. The response is "effectively a jump", and "the exchange rate returns subsequent to the few minutes around the time of the data release are orthogonal to the unexpected component" (P-K3-032-b): no drift to trade after D9.5a's 2-minute guard. A fill in the release minute is the gapped-market case of D9.4. The release clock enters K3-ml-01 as nfp_phase only |
| X-06 K3-fomc-01 | 6E or 6J traded on FOMC target and path surprises, or a fade of the "short-lived" reaction (K3-009 P-K3-009-a) | Partition rule 4 (K8); rule 1 | The surprise is measured from a rates instrument (fed funds futures), so the member has a rates leg: K8 (section 4). A price-proxy fade has no logged horizon or threshold (abstract only; numbers [unverified]). The clock enters K3-ml-01 as fomc_phase |
| X-07 K3-ukrel-01 | 6B before UK CPI, industrial production and retail sales (pre-release drift), or after them (the "slower" adjustment) (K3-034 P-K3-034-a) | Rule 1 (evidence) | The source's own finding is that the pre-release drift "weakens with the end of the prerelease access" in 2017, before this program's windows (2019+). The post-release claim is relative ("the speed of adjustment has become slower") and comes from an abstract with no horizon, magnitude or signal rule. The UK release time is not in the log. The product is "presumably 6B" but [unverified] |
| X-08 K3-payroll-01 | Mimic speculators' FX futures positioning ahead of payroll news (K3-014 P-K3-014-a) | Rule 3; flat by F | The positioning data are "most likely the CFTC weekly trader reports (not confirmed)" (K3-014 block), a weekly series. The information is "long-lived", which points to multi-day holding. No intraday rule is traceable |
| X-09 K3-spotlead-01 | 6E or 6J traded on a spot-FX lead (EBS or retail spot leading the future), or the reverse (K3-026 P-K3-026-a; K3-027 P-K3-027-a; K3-029 P-K3-029-a; K3-031, K3-037 title only) | Rule 3; D9.3/D9.4; rule 1 | Interdealer spot (EBS, Reuters) is proprietary, and a free retail feed is indicative quotes. The sources disagree on which market leads (K3-027: spot leads; K3-026 and K3-029: futures lead or dominate). Price-discovery shares imply second-to-minute horizons, not a traceable minute-scale rule with a threshold |
| X-10 K3-triarb-01 | Triangular arbitrage among EUR, JPY and CHF legs (K3-044 P-K3-044-a, b; K3-045 P-K3-045-a) | D9.3 floor; D9.4 | Opportunities last seconds, and profiting needs beating others "to an unfeasibly large proportion of arbitrage prices" (P-K3-044-a). Topstep's prohibited pattern is "average durations measured in seconds" (F7.3). The three-leg version would also breach the 1 lot-equivalent cap |
| X-11 K3-xrate-01 | Lead-lag or relative value among CME currency futures (cross rates such as EUR/GBP from 6E and 6B) (K3-042) | Rule 1 | Title only; nothing retrieved. No other log item gives a cross-rate rule |
| X-12 K3-gaprev-01 | Intraday reversal after large one-day returns and opening gaps (K3-011 P-K3-011-a, b) | Rule 1 (parameters) | Abstract only. The "large" thresholds and magnitudes are [unverified], and the pattern is from 1988-2003 pit sessions (the "opening gap" of the pit open no longer exists). The prior-day daily-bar family on FX is CP3 (which bets the other way, continuation) |
| X-13 K3-mehedge (GBP, AUD, CAD, CHF, NZD) | K3-mehedge-01 extended to the other currencies in the source's sample (K3-001 block: EUR, JPY, GBP, CAD, AUD, SEK, NOK, CHF, NZD) | Rule 3 (data) | No free historical source of the local benchmark index (FTSE, S&P/ASX 200, S&P/TSX, SMI, NZX 50) was named or confirmed in E.0: the search tools are exhausted. The source's Datastream indices are proprietary. If E.2 names one, the lead may add that exposure (+1 trial each) |
| X-14 K3-fixrevON-01 | K3-001's post-fix reversion as tested, from 16:00 GMT to noon the next day (P-K3-001-c) | Flat by F | The position would be held overnight. A same-day truncation (16:00 London to 15:05 CT) is an untested horizon. The month-end post-fix reversal enters as K3-ldnrev-01 (at K3-002's 15-minute horizon), and the all-days pre-fix-hour return enters K3-ml-01 as ldn_prefix_ret |
| X-15 K3-fomcdrift-01 | Currency futures positioned on FOMC shocks over "three weeks before and after the announcements" (K3-008 P-K3-008-a) | Flat by F | Multi-week drift; whether the announcement-day effect is intraday is [unverified] (abstract only). The high-yield and EM emphasis points to 6M, which is out by D1 |
| X-16 K3-cot-01 / K3-carry-01 | Weekly COT positioning predicting spot rates (K3-015 P-K3-015-a, b); carry and order flow (K3-012 P-K3-012-a) | Flat by F | Weekly signals and multi-week horizons; carry is held overnight (partition rule 8). Both items are logged as should-have-been-rejected |

---

## 3. Beyond budget (lead decides)

None. The log supports 6 new members inside the budget of 11. These candidates were considered and not
written; none is a budget overflow. Each would add trials.
- **Ranaldo's fixed 4-hour blocks for CHF and JPY** (K3-024 P-K3-024-d):
  - The windows: CHF short 08:00-12:00 GMT and long 12:00-16:00 GMT; JPY long 12:00-16:00 GMT.
  - Why not written: the only cost evidence on these pairs is against them. "most of these simple
    time-of-day trading strategies are not profitable when trading costs are included. However, the
    notable exception is EUR/USD" (K3-023 P-K3-023-b). Ranaldo's figures are gross, on indicative
    quotes. The EUR version of the mechanism is carried by K3-ecbfix-01, which is in the same direction
    in overlapping hours.
  - Cost: +2 trials (+1 for a GBP or AUD version from K3-023, which the same cost passage argues
    against).
- **The London-fix W for GBP** (K3-016's pre/post-London trade): its own CME test on 6B is negative,
  "-4.83" % a year, Sharpe "-0.51" (P-K3-016-f). +1 trial.
- **The every-day pre-Tokyo long-dollar trade on 6J** (K3-016): its own CME test is "-11.23" % a year
  (P-K3-016-f). The gotobi-conditioned version is written (K3-tkypre-01). +1 trial.
- **K3-ecbfix-01 as the pre-fix leg only.** The source's table gives the pre-leg alone a Sharpe of 0.99
  against 0.65 for the headline pre/post trade (P-K3-016-f). The headline trade is written, so as not to
  pick the best of the source's nine cells. The lead may substitute (not add) the pre-leg-only version:
  0 extra trials.
- **K3-ldnrev-01 for AUD and CAD.** Both are in K3-002's pair list, but their post-reform month-end
  cells are not in the log. K3-003 is positive "for at least one horizon" in all but JPY and GBP
  (P-K3-003-e), which is pre-reform. +2 trials.

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Alquist, Ellwanger, Jin (2020), JFM (registry K4-008, tagged K1-K4; not read by K3) | WPSR-identified oil shock (K4) -> FX (K3), equities, Treasuries | oil inventory news as an instrument for cross-asset responses (K3 log section 4, run 1) |
| Aligrithm, "FX Edge Lives in Other Markets (cross-asset series)" (Quantocracy; practitioner) | government-bond rates (K2) -> FX (K3) | interest-rate-parity signal on a graph (K3 log section 4) |
| Peng, Chollete, Hughen, Lu (2026), "Forecasting Volatility of Currencies and Oil with Brown Firms" (R-K3-028) | equities -> FX and crude volatility | cross-asset volatility forecast (K3 log section 4) |
| Quantpedia slugs "equity-momentum-spillover-to-currencies", "stock-and-bond-returns-predict-currency-returns" (pages HTTP 500) | equity (K1), bonds (K2) -> FX (K3) | cross-asset; horizon unknown (K3 log section 4) |
| Wang, Yang, Simpson (2008), K3-009, the surprise measure | fed funds futures surprise (rates) -> FX futures (K3) | X-06: the FOMC target and path surprise is a rates-instrument signal |
| Kurov, Stan (2018), K3-035 [K3] | monetary-policy uncertainty (a rates-derived measure, [unverified]: abstract only) conditioning FX's macro response | conditioning variable from rates; K3 has no macro-release base member to condition (X-05) |
| Sharma (arXiv 1705.08022), flagged by the K2 reader (K2 log) | 10-year Treasury yield (K2) -> AUD, CAD, NZD, JPY pairs (K3) | macro-forecast input to an FX pairs trade |
| Rosa (2013), K4-025, flagged by the K4 reader | FOMC-driven USD (K3) and CL (K4) | the energy response to FOMC runs through the dollar |
| Quantocracy / Milton FMR, "Pairs Trading ... CAD - Crude Oil", flagged by the K4 reader | 6C (K3) and CL (K4) | CAD-crude pairs |
| Zangelidis, Rezitis (2026), flagged by the K1 reader | US dollar index (K3) with NASDAQ, copper and commodity indices | intraday realized-volatility topology |

The first four rows are the K3 reader's own flags. Rows 5 and 6 are this catalog's routing of X-06
and K3-035. Rows 7-10 are other readers' flags naming a K3 leg, listed for completeness.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K3.md section 3 (K3-001 to K3-045), every
`[K3]`-tagged passage elsewhere (K2-015), and the panel item the log points to (D.1 A10).

| Item | Disposition |
|---|---|
| K3-001 Melvin, Prins | **Used:** K3-mehedge-01 (P-a, b, d, e); K3-ml-01 ldn_prefix_ret (P-c) and month_end (P-a, e); supporting K3-ldnrev-01 (P-c, month-end reversion twice as large). **Not intraday-feasible as tested:** the reversion to next-day noon, X-14. Other currencies excluded for data, X-13 |
| K3-002 Ito, Yamada (London) | **Used:** K3-ldnrev-01 (P-b, d, e, f, g; P-a context); T_L window reasoning in K3-ldnmom-01 and K3-mehedge-01 (P-d); K3-ml-01 month_end (P-b, f). The intra-month null (P-f, g) is why ldnrev trades month-end only. P-c (tail probability) not used |
| K3-003 Evans (WMR fix) | **Used:** K3-ldnrev-01 (P-b, c, d, f); the JPY and GBP exceptions (P-e) as conflicting evidence and in the GBP exclusion; K3-ml-01 month_end (P-b) |
| K3-004 Xu, Øwre-Johnsen (Norges Bank) | **Supporting and conflicting:** activity rises ahead of the ECB fix (P-b, context for K3-ecbfix-01); no significant price change at the WM fix (P-d, evidence against K3-ldnmom-01). The NOK result concerns a non-K3 product. P-a, P-c are context only |
| K3-005 Bessho, Sugimoto, Suzuki (gotobi) | **Used:** K3-tkypre-01 (P-a, P-c). Leg 2 excluded, X-02 (P-b, P-d look-ahead). The 3:00 JST entry and the golden-cross filter are excluded, X-03 |
| K3-006 Baldwin, Lewejohann (CME Asian hours) | **Not a mechanism:** a liquidity and cost input. Cited in C12 (P-a, b, c) as context for the overnight coverage check of K3-tkypre-01, K3-tkypost-01 and K3-ml-01 |
| K3-007 Baum, Kurov, Wolfe (Chinese PMI) [K3] P-b to P-g | **Excluded,** X-04. P-b's quotation convention is used in C8 and in K3-ml-01 dol_ret60. The [K1], [K4], [K5], [K6] passages belong to those writers |
| K3-008 Tse (FOMC, currency futures) | **Not intraday-feasible** (multi-week), X-15 |
| K3-009 Wang, Yang, Simpson (FOMC surprises) | **Excluded as a member,** X-06 (surprise from rates: K8). Used in K3-ml-01 fomc_phase (P-a) |
| K3-010 Seeck (intraday momentum, 6J) | **Covered by CP1** (family C3, intraday momentum). The London-open variant is not written: the passages are first-run and not re-verified, and the source reports that 6J "fail[s] to clear [its] cost hurdle" (P-a) |
| K3-011 Rentzler, Tandon, Yu | **Excluded,** X-12 (abstract only, thresholds absent, pit era) |
| K3-012 Breedon, Rime, Vitale (carry) | **Not intraday-feasible,** X-16 |
| K3-013 FSB FX Benchmarks | **Not a mechanism.** Used for context: the fix minute's volume (P-d) in K3-ldnrev-01's D9.4 check; the 8:30 ET release as the day's peak one-minute volatility (P-b), which informed K3-ml-01's window placement |
| K3-014 Park (payroll positioning) | **Excluded,** X-08 |
| K3-015 Tornell, Yuan (COT) | **Not intraday-feasible,** X-16 |
| K3-016 Krohn, Mueller, Whelan | **Used:** K3-ecbfix-01 (P-a, c, d, e, f, g, h); K3-tkypost-01 (P-b, c, d, f); clocks T_L, T_E, T_T (P-c); K3-ml-01 fix_phase and dol_ret60 (P-a, b); evidence against K3-tkypre-01's every-day analogue (P-f). The GBP London W and the every-day pre-Tokyo trade are not written, for negative CME results (section 3) |
| K3-017 Osler, Turnbull | **Used:** K3-ldnmom-01 (P-a, b, c); the 15:45 anchor in K3-ldnrev-01's signal window (P-b) |
| K3-018 Marsh, Panagiotou, Payne | **Supporting** K3-ldnrev-01 (P-a (2), (6); P-b, c: CME futures data); evidence against K3-ldnmom-01's post-fix part (P-a (6)) |
| K3-019 Evans, O'Neill, Rime, Saakvitne (FCA) | **Conflicting evidence** for K3-ldnrev-01, stated in its entry (P-a, b, c). Its "less trading before the fix" (P-a) is stated against K3-ldnmom-01. Its 15-minute windows (P-b) set ldnrev's pre-fix window |
| K3-020 Benenchia, Galati, Lepone | **Pending evidence:** Stage 2's reversal result is [unverified] (P-c). Its 15-minute windows (P-a) support ldnrev's pre-fix window. Section 7, item 7 |
| K3-021 Michelberger, Witte | **Supporting** K3-ldnmom-01 (P-a, c). The 10am EST expiry cluster (P-b) informed K3-ml-01's window placement |
| K3-022 Ito, Yamada (Tokyo) | **Used:** K3-tkypre-01 (P-a, b, d); conflicting evidence for K3-tkypost-01 (P-c); the 5/5-minute switch excluded, X-01 (P-c); T_T clock (P-c) |
| K3-023 Breedon, Ranaldo | **Corroborates** K3-ecbfix-01 (P-a, b, c). CHF, JPY, GBP and AUD versions not written: its cost result (P-b) is against them (section 3). P-d (Cornett et al., second hand) is corroborating. P-e (the July 4 anecdote) is insufficient evidence: an anecdote, not a test |
| K3-024 Ranaldo | **Corroborates** K3-ecbfix-01 for EUR (P-a, b, c, d). The CHF and JPY block member was considered and not written (section 3) |
| K3-025 Cornett, Schwarz, Szakmary | **Corroborates** K3-ecbfix-01's second leg (P-a; abstract only, 1977-1991 pit session). Insufficient evidence for a member of its own |
| K3-026 Tse, Xiang, Fung | **Excluded,** X-09 (lead-lag) |
| K3-027 Cabrera, Wang, Yang | **Excluded,** X-09 |
| K3-028 Han, Kling, Sell | **Insufficient evidence:** day-of-week volatility patterns with no directional claim (P-a), pit-era. Not used |
| K3-029 Chen, Gau (2022) | **Excluded** as a lead-lag member (X-09) and as a surprise member (X-05). Used in K3-ml-01 nfp_phase (P-a: "nonfarm payroll affect both order flows and exchange-rate changes") |
| K3-030 Martínez, Tse [K3] P-a | **Used:** K3-ml-01 heat_wave_rv (P-a, "intraregion volatility (heat waves)"). The [K1] and [K2] parts belong to those writers |
| K3-031 Chen, Gau (2010) | **Insufficient evidence:** title only. Listed under X-05 and X-09 |
| K3-032 Chaboud et al. (IFDP 823) | **Excluded as a member,** X-05 (no post-release drift, P-b). Used in K3-ml-01 nfp_phase (P-b, c) and window placement (P-a); T_L confirmation (P-a) |
| K3-033 Cai, Howorka, Wongswan (IFDP 863) | **Used:** K3-ml-01 heat_wave_rv (P-a) |
| K3-034 Kurov, Sancetta, Wolfe | **Excluded,** X-07 |
| K3-035 Kurov, Stan [K3] P-a | **Routed to K8** (section 4). No K3 base member to condition |
| K3-036 Andersen, Bondarenko, Gousgounis, Onur | **Insufficient evidence:** title only (FX futures invariance, cost modelling). Not used |
| K3-037 Cabrera | **Insufficient evidence:** title only. Listed under X-09 |
| K3-038 Cotter, Dowd | **Insufficient evidence:** a one-week 1997 sample, descriptive (P-a, b). Not used |
| K3-039 Batten, Ellis, Hogan | **Insufficient evidence:** 42 days of indicative quotes, descriptive (P-a, b). Not used |
| K3-040 Kosowski et al. | **Insufficient evidence:** title only, content [unverified]. CP1's (a) form bets the opposite way (overnight continuation) |
| K3-041 Khademalomoom, Narayan | **Corroborating** the session-clock family (P-a: time-of-day effects in AUD, GBP, CAD, EUR, JPY, CHF). Abstract only, no windows or magnitudes: insufficient evidence for a member of its own |
| K3-042 Elyasiani, Kocagil | **Excluded,** X-11 (title only) |
| K3-043 Ayadi, Ben Omrane, Das | **Insufficient evidence:** title only. It concerns EM currencies; 6M is out by D1 |
| K3-044 Fenn et al. | **Excluded,** X-10 |
| K3-045 Aiba et al. | **Excluded,** X-10 |
| K2-015 Andersen, Bollerslev, Diebold, Vega, P-K2-015-a [K3] (and P-c's implicit FX comparison) | **Not a member:** a contemporaneous "conditional mean jump" (X-05). Used in K3-ml-01 nfp_phase |
| D.1 A10 Baltussen, Da, Lammers, Martens (panel, not re-read) | **Covered by CP1.** Its FX results are [unverified from K3's side] (K3 log) |
| reports/stage_e0_research_K3_sonnet_partial.md | Not used (superseded, per the brief) |
| R-K3-001 to R-K3-044 | Rejected in the log; not used. Facts from three of them are used: R-K3-013 (ECB fix time, now confirmed from the ECB page: "around 14:10 CET"), R-K3-014 (FX BTIC routes month-end fix flow to CME futures, in K3-mehedge-01), R-K3-015 (CME "Daily Settlement 2:00 p.m. Central Time", in C5) |

**Correlated members, flagged for the lead's Tier-A accounting (not duplicates).**
- **London fix, EUR, JPY and CHF on month-end days:** K3-mehedge-01 (T_L-60 to T_L-3), K3-ldnmom-01
  (T_L-12 to T_L+5) and K3-ldnrev-01 (T_L+5 to T_L+20) trade adjacent windows. Their signals and
  directions are independent by construction.
- **6J on gotobi evenings:** K3-tkypre-01 (SELL into the fix) and K3-tkypost-01 (BUY after it) trade
  consecutively.
- **K3-ecbfix-01 and K3-ml-01** both read the EUR fix clock; K3-ml-01's fix_phase feature encodes the
  same W.

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all seven admitted) |
|---|---|---|---|
| K3-cp1-01 | EUR, AUD, GBP, CAD, JPY, CHF, NZD | 1 | 7 |
| K3-cp2-01 | EUR, AUD, GBP, CAD, JPY, CHF, NZD | 1 | 7 |
| K3-cp3-01 | EUR, AUD, GBP, CAD, JPY, CHF, NZD | 1 | 7 |
| K3-ldnrev-01 | EUR, JPY, CHF | 1 | 3 |
| K3-ldnmom-01 | EUR, JPY (narrowed by the lead from 6) | 1 | 2 |
| K3-mehedge-01 | EUR, JPY (each only with an obtained index history) | 1 | 2 |
| K3-ecbfix-01 | EUR | 1 | 1 |
| K3-tkypre-01 | JPY | 1 | 1 |
| K3-tkypost-01 | JPY | 1 | 1 |
| ~~K3-ml-01~~ [excluded, U6] | EUR (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **36** = 21 port + 14 new + 1 ML |

**General formula.** With E the number of admitted exposures and a_X = 1 if exposure X is admitted
(0 otherwise):

N_K3 = 3E + 5 a_EUR + 5 a_JPY + 2 a_CHF + a_GBP + a_CAD + a_NZD - (index drops from K3-mehedge-01).

- a_EUR's 5 = ldnrev + ldnmom + mehedge + ecbfix + ml.
- a_JPY's 5 = ldnrev + ldnmom + mehedge + tkypre + tkypost.
- a_CHF's 2 = ldnrev + ldnmom. GBP, CAD and NZD carry ldnmom only; AUD carries only the ports.
- Check: 21 + 5 + 5 + 2 + 1 + 1 + 1 = 36.
- **Examples:** if D2 admits only 6E, 6J and 6B (and both indices are obtained), 9 + 5 + 5 + 1 = 20.
  If neither index is obtained, subtract 2.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **M6E and M6A carry an unresolved * restriction** (D9.8; F12.1 found no referent).
   - D2 may pick M6E for EUR or M6A for AUD. Every EUR and AUD member carries the flag, and K3-ml-01
     trades EUR with no fallback.
   - If the user cannot clear the flag before E.1, D2 must choose among 6E and E7 for EUR, and 6A
     alone for AUD.
2. **Overnight windows are outside D1's coverage measurement** (C12). K3-tkypre-01 and K3-tkypost-01
   trade 6J at 17:30-01:00 CT; K3-ecbfix-01 and K3-ml-01 trade the EUR vehicle from 01:00 and 00:46 CT.
   D9's member-level coverage check decides in E.2. If it fails, those members are excluded before
   screening; the catalog does not assume it passes.
3. **K3-ldnmom-01 rests on a model, not a profitability test** (P-K3-017-b; the K3-017 block), and
   has contrary evidence (P-K3-019-a, P-K3-004-d). It costs 6 trials. The lead may cut it, or narrow
   it to month-end days (fewer events, with the flow evidence of P-K3-001-e).
4. **K3-mehedge-01's signal sources are unconfirmed** (header; X-13).
   - The member is written for EUR (EURO STOXX 50) and JPY (Nikkei 225), with an E.2 drop rule.
   - The index choice (the publishers' blue-chip indices instead of the source's Datastream Total
     Market indices) is a judgment for the lead to accept or change.
   - The other five exposures need a named free source.
5. **K3-ecbfix-01's form.** The headline pre/post trade is written. The pre-leg-only version (Sharpe
   0.99 in the source's table against 0.65) is available as a substitution (section 3).
6. **Month-end and holiday definitions** (C9). Three are judgments:
   - ME is CME's last trade date of the month, with a drop when it is an E&W bank holiday (whether the
     WM/R month-end flow happens on a London holiday is not in the log);
   - London members skip E&W bank holidays;
   - Tokyo business days exclude 31 December to 3 January, and gotobi dates are not shifted off
     weekends or holidays (the log states no shift rule).

   Any change moves a few dates a year.
7. **Is the post-fix reversal still alive?** K3-019 (reversals gone after 2015, all days) and K3-002
   (month-end profitable post-reform at 15 minutes) conflict, and the decisive pre-registered re-test
   (K3-020 Stage 2, 2015-2023) was not retrieved (SSRN, ScienceDirect and Macquarie blocked, Firecrawl
   exhausted). If a later session retrieves it and it finds no month-end reversal, the lead may cut
   K3-ldnrev-01 (3 trials) before E.1 hashes the catalog.
8. **The cost sample has no fix-event days.** D8's five dates include no month-end, so the month-end
   fix window's spread is calibrated on ordinary days, which may understate K3-ldnrev-01's and
   K3-mehedge-01's cost. One date, 2026-04-15, is a gotobi day. The lead decides whether to add a
   month-end date to the K3 mbp-1 sample (a small spend, quoted in E.1) or to accept the limitation, as
   was ruled for K4's gas Thursdays (Q5, 21:52).
9. **Port text meets FX release clocks, copied unchanged:**
   - CP2's opening range [07:20, 07:35) contains the 07:30 CT BLS release on NFP days.
   - CP1's entry fill at 13:30 on FOMC days sits exactly 30 minutes after the statement. That is the
     boundary of D8's event-window cost; E.2 must fix whether the window is [release, release + 30 min)
     or closed.
   - Whether FX ports skip these days would be a D6 change.
10. **Frequency** (C10). K3-ldnrev-01 and K3-mehedge-01 trade about 14 research days and need about
    22 x eps_X per event. They are likely "inconclusive by design" (D4). They cost 5 trials. The 21:52
    ruling (Q4) keeps such members; this is noted for the trial budget only.
11. **E.2 checks named in this catalog:**
    - (a) The known-answer tests for T_L, T_E and T_T (C9).
    - (b) EC-TGT for 2019-2025 from Wayback captures.
    - (c) The equity-index histories (K3-mehedge-01).
    - (d) Tick-size history 2019-2026 (C7) and E7's listing date (C8).
    - (e) How TopstepX counts E7, M6E, M6A and M6B against the lot limit (C6).
    - (f) CME FX price limits against D9.7 (C11).
    - (g) Overnight member-level coverage (C12).
    - (h) The set S for K3-ml-01's dol_ret60, frozen before any fit.
    - (i) The Japanese year-end closure (C9).
12. **Registry hygiene** (already listed by the reader, K3 log section 5):
    - Wrong or incomplete author fields: K3-018 (correct: Marsh, Panagiotou, Payne); K3-005, K3-012,
      K3-014, K3-015, K3-038 and K3-039 "unspecified"; K3-040 and K3-043 "?".
    - Run 1 edited K3-007 and K3-009 in place.
    - This catalog cites the corrected authors from the log blocks.

---

# Cluster K4

# Stage E.0 hypothesis catalog, cluster K4 (energy: CL, QM, MCL, NG, QG, MNG, RB, HO)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K4-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials.
> **K4 after the decisions: 8 active members, 19 confirmation trials** (5 new + 3 core ports (K4-ngrev-01 excluded on review R-06); 12 port + 7 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K4-OpusXHigh (Stage E.0 Task 4), 2026-09-23, from about 21:30 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K4 product existed on this machine. It uses only these product-specific numbers:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- event-calendar metadata: EIA release dates and clock times, and the API release-time rule.

Calendar metadata carries no prices. No price level, range or volatility of any product is used or
assumed anywhere below.

**Inputs read in full:**
- reports/stage_e0_research_K4.md. The superseded sonnet log was not used.
- Every `[K4]`-tagged passage in the other logs: K3-007, K3-035 and K3-040 in
  reports/stage_e0_research_K3.md; K5-028 and K5-029 in reports/stage_e0_research_K5.md. The K2, K6
  and K7 logs hold none.
- reports/stage_e0_source_registry.jsonl (K4 lines and every line tagged K4).
- docs/STAGE_E_DESIGN.md (D1-D15, with the 21:12 amendments to D2 and D6).
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md.
- reports/stage_e0_liquidity.json (K4 rows).
- reports/stage_d1f_confirmation_list.md 2.1 A3.
- strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py.
- strategy/research/h_daily_bar/h6_prior_close_location.py.
- reports/stage_d1b_family_f_declaration.md F3.3.
- The D.1 literature log, row B4 only (K4-013 points there). The row is truncated in that file.
- reports/stage_e0_catalog_K2.md, for format only.

**Official pages fetched in this task** (curl, 2026-09-23 about 21:35-21:41 PDT). They were fetched
only to confirm release-time sources; no mechanism research was done:
- https://www.eia.gov/petroleum/supply/weekly/schedule.php (HTTP 200). It holds the 2024-2026
  exception table: "The standard release time and day of the week will be at 10:30 a.m. eastern time
  on Wednesdays with the following exceptions."
- https://ir.eia.gov/ngs/schedule.html (HTTP 200). It holds the 2025-2026 table: "The standard release
  time and day of the week will be at 10:30 a.m. eastern time on Thursdays with the following
  exceptions."
- Wayback CDX listings of both pages, which show one or more captures in every year 2019-2026
  (timestamps in C9). Two captures were opened:
  - http://web.archive.org/web/20200207151454/https://www.eia.gov/petroleum/supply/weekly/schedule.php
    (2019-2020 table);
  - http://web.archive.org/web/20210104203613/https://ir.eia.gov/ngs/schedule.html (2020-2021 table).
- https://www.eia.gov/petroleum/supply/weekly/archive/ (HTTP 200). Title "Weekly Petroleum Status
  Report Archives"; it lists release dates by year, 2011-2026.
- https://ir.eia.gov/ngs/ngs.html (HTTP 200). It links /ngs/ngshistory.xls and /ngs/schedule.html,
  with no archive of release dates.
- https://ir.eia.gov/ngs/archive.html (HTTP 403) and https://www.eia.gov/naturalgas/storage/archive/
  (HTTP 404).

---

## 0. Header

| Item | Value |
|---|---|
| Products | CL, QM, MCL, NG, QG, MNG, RB, HO (NYMEX; Topstep F1 "CME NYMEX Futures") |
| Exposures | WTI crude {CL, QM, MCL}; Henry Hub gas {NG, QG, MNG}; RBOB {RB}; ULSD {HO} (partition section 1) |
| D1 | **D1 applied: all four K4 exposures IN** (design D1 table). Admissible vehicles, 2026 Jan-Aug ADV: crude CL 1,079,857, MCL 252,100, QM 9,446; gas NG 521,792, MNG 14,942, QG 4,060; RB 206,850; HO 187,479 (the D1 table's figure) |
| Members | 10 = 6 new + 3 core ports + 1 ML member. Budget 15, so 5 slots are unused (section 3) |
| Trials in N (confirmation) | **21 if D2 admits all four exposures:** 12 port + 8 new + 1 ML. In general 3E + 5a_C + 3a_G + a_H, where E is the number of admitted exposures and a_C, a_G, a_H are 1 if crude, gas and ULSD are admitted (0 otherwise). Example: without RBOB and ULSD, 14 |
| ML grid | ~~48 configurations, counted only in the K4 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Starred products | **MCL** (Topstep F1: "Micro Crude Oil (MCL)*"). Its restriction is unresolved (D9.8; topstep facts F2 "not published"). Every crude member carries the flag. CL, QM, NG, QG, MNG, RB and HO are unstarred |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. RB and HO each have one full-size contract. CL and NG may fail rho <= 2.0 at q = 1, leaving MCL/QM and MNG/QG as the vehicles. RB and HO may go untraded. Every entry is written for every exposure its evidence names, each marked **"traded only if D2 admits the exposure"** |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose
  ts_event (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values
  are usable from then on. Eastern-time releases convert to CT by subtracting one hour, since both
  zones change clocks on the same dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine
  convention D6 and D15.3 use). "Market intent on the bar at X" fills at the open of the bar at
  X + 1 min.
- **C3 Trade date.** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). The energy Globex
  session opens at 17:00 CT, so the first bar of trade date d is the 17:00 CT bar of d-1 (Sunday for
  a Monday).
- **C4 Exclusions for the six new members.** The ports follow D6 as written. A new member does not
  trade on:
  - roll-blackout dates (program convention, `screen_candidate` with `roll_blackout`);
  - dates the D10 energy calendar marks as early close or early halt ("Days with early_halt_ct set:
    no trade", Family H);
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which the signal bars
    of one computation carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
  flatten at F is the backstop. A CME circuit-breaker halt shows up as missing bars and is handled
  by the same rules.
- **C5 Flat time.** F = 15:08 CT (D9.1; D6 energy row: O = 08:00, C = 13:30, F = 15:08). No new
  member's last fill is later than 14:59 CT.
- **C6 Size.** q_c of the exposure's D2 vehicle, at most 1 lot-equivalent (D2 amended 21:12; D9.5).
  - Lot weights (D9.6): CL, QM, NG, QG, RB and HO count 1 each ("minis 1"). MCL and MNG count 0.1
    each.
  - Topstep's special-weighting list names only SIL, MBT and MET (F5), so no special weight for QM
    or QG is published. E.2 confirms how TopstepX counts them.
  - So q_c = 1 for a full-size or E-mini vehicle, and q_c <= 10 for a micro.
  - No member sizes by signal.
- **C7 Ticks and fees.** Tick sizes and values are from reports/stage_e0_liquidity.json (CME
  contract specifications, fetched 2026-09-23 20:33-20:47 PDT). Round turns are Topstep F3. The
  2026-10-01 fee rise is applied as D8 does.

  | Contract | Exposure | Tick | Tick value | Topstep round turn | Lot-equivalent |
  |---|---|---|---|---|---|
  | CL | crude | 0.01 | $10.00 | $4.02 | 1 |
  | QM | crude | 0.025 | $12.50 | $3.42 | 1 (E.2 confirms) |
  | MCL* | crude | 0.01 | $1.00 | $1.52; $1.72 from 2026-10-01 (D8) | 0.1 |
  | NG | gas | 0.001 | $10.00 | $4.22 | 1 |
  | QG | gas | 0.005 | $12.50 | $2.02 | 1 (E.2 confirms) |
  | MNG | gas | 0.001 | $1.00 | $1.72; $1.92 from 2026-10-01 (D8) | 0.1 |
  | RB | RBOB | 0.0001 | $4.20 | $4.02 | 1 |
  | HO | ULSD | 0.0001 | $4.20 | $4.02 | 1 |

  These are 2026 specifications. E.2 must confirm that each tick was unchanged over 2019-05..2026-06
  before any bar is read, because CP2's buffer and several ML features are in ticks.
- **C8 Price data.** Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is
  bought in E.1, and the confirmation and holdout-2 history of the chosen vehicle in E.2b (D13).
  - **History.** CL, QM, NG, QG, RB and HO from 2019-05. MCL was listed 2021-07-12 and MNG
    2023-11-06 (liquidity JSON listing dates). Earlier months quoted as "None of the symbols could
    be resolved" (D13).
  - **Short micro histories.** A micro vehicle's own confirmation history is therefore short. D2 and
    D4 let E.2 declare the full-size contract's bars as the price path, per exposure, before any
    confirmation read.
  - **Availability.** A bar is available at its close (C1).
  - **Tick-free rules.** Every new-member rule that compares a price change with a level uses a
    percent return or a sign, so it gives the same decision on any contract of an exposure. The
    tick-denominated quantities are CP2's buffer and the ML features (section 7, item 2).
  - **mbp-1** enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C9 Event calendars.** All are external and free. Each rule reads only dates and scheduled clock
  times, never a released inventory value.
  - **EC-WPSR, EIA Weekly Petroleum Status Report release schedule.**
    - **Standard slot:** "10:30 a.m. eastern time on Wednesdays" = 09:30 CT (P-K4-017-b; confirmed
      on the page above).
    - **Exceptions:** holiday weeks move the release, for example 2019 "Thursday 11:00 a.m." (10:00
      CT, Wayback 2020 capture) and 2025-2026 "Thursday 12:00 p.m." (11:00 CT). One exception is
      "December 29, 2025 Monday 5:00 p.m." (16:00 CT, after F, so no member can trade it).
    - **Sources:** the current page, plus yearly Wayback captures 20190110082341, 20200207151454,
      20210120153010, 20220114004832, 20230113222513, 20240118235307, 20250110211433 and
      20260118223951.
    - **Actual publication dates:** https://www.eia.gov/petroleum/supply/weekly/archive/ (release
      dates by year).
    - **Notation:** T_W(d) is the release time in CT on d.
  - **EC-NGS, EIA Weekly Natural Gas Storage Report schedule.**
    - **Standard slot:** "10:30 a.m. eastern time on Thursdays" = 09:30 CT (P-K4-018-a).
    - **Exceptions:** for example "11/25/2020 Wednesday 12:00 p.m." (11:00 CT), "1/3/2020 Friday
      10:30 a.m.", "December 29, 2025 - (Updated) Monday 12:00 p.m."
    - **Sources:** the current page, plus yearly Wayback captures 20190111124957, 20200128214849,
      20210104203613, 20220114160745, 20230210074654, 20240607000738, 20250117233342 and
      20260126101407.
    - **Actual publication record:** E.2 sources it (for example Wayback captures of
      ir.eia.gov/ngs/ngs.html). ir.eia.gov/ngs/archive.html returned 403.
    - **Notation:** T_N(d) is the release time in CT on d.
  - **Availability rule for EC-WPSR and EC-NGS.**
    - **Timing:** each year's exception table is available early in the year. The captures listed
      date from January or February, except the 2024 storage capture (June).
    - **Mid-year changes** exist (the "(Updated)" entries). When each one was posted is not known
      here, hence the drop rule below.
    - **E.2 builds each table** from the last capture before each release, and cross-checks it
      against the record of actual publication.
    - **Dropped releases:**
      - a release whose actual date or time differs from its schedule entry;
      - a release marked "(Updated)" for which no capture dated before the member's entry time shows
        the update.

      A rule may time itself only on a release time it could have known that morning.
  - **EC-API, American Petroleum Institute bulletin timing (the rule only; no API data is read by
    any member).**
    - **The rule:** "the weekly reports are scheduled for release every Tuesday afternoon at
      approximately 4:30 pm Eastern. If Monday is a Federal holiday, the reports are scheduled for
      release on Wednesday afternoon" (P-K4-045-a), that is, Tuesday about 15:30 CT.
    - **Standard week (definition):** the WPSR is in its standard Wednesday 10:30 ET slot (not in
      that year's exception table), and the Tuesday before it is a full-session trade date in
      EC-CAL.
    - **Why the Monday-holiday case should drop out:** in the WPSR tables read here (2019-2020 and
      2024-2026), every Monday federal holiday moves the WPSR off its Wednesday slot. For example,
      in 2019 "Martin Luther King Jr.", "President's", "Memorial", "Labor", "Columbus" and
      "Veterans" each moved it to "Thursday 11:00 a.m.". So a standard week should never have the
      Wednesday API case. The 2021-2023 tables were not opened in E.0.
    - **E.2 check:** drop any standard week whose Monday is a US federal holiday, whatever the table
      says.
  - **EC-CAL.** The D10 energy calendar (trade dates, holidays, early closes and halts), built by
    E.2 from CME schedules.
  - **EC-NYSE.** NYSE full closures and early closes, used only by K4-eiamom-01. Free and published
    in advance. Not fetched in E.0; E.2 sources it (nyse.com hours-calendars, through Wayback for
    past years).
- **C10 Non-positive prices.** The log records a one-off WTI event on 2020-04-20 (R-K4-061,
  "Arbitrage breakdown in WTI crude oil futures: An analysis of the events on April 20, 2020").
  - That the front contract then traded at non-positive prices is a public fact not verified in
    E.0. E.2 sees it in the bars, if it is there.
  - Every percent return below is (P1 - P0) / P0 and requires P0 > 0; otherwise the rule does not
    trade.
  - Tick differences, the ports and the ML features are unaffected.
- **C11 Frequency (arithmetic from calendar counts, no price data).**
  - **Research window:** 2025-04-01..2026-06-19 has 319 weekdays (about 305 CME trade dates), 64
    Wednesdays and 64 Thursdays. Eight WPSR exceptions fall inside it (2025-05-29, 09-04, 10-16,
    11-13, 12-29; 2026-01-22, 02-19, 05-28), so there are about 56 standard-Wednesday releases.
    About 64 storage releases fall inside it, 5 of them off the Thursday slot (2025-06-18, 11-14,
    11-26, 12-29, 12-31).
  - **Confirmation window:** 2019-05-06..2024-02-29 (the earliest S_X) has 1,259 weekdays and 252
    Wednesdays.
  - **Consequence:** a member trading on k of about 305 research dates, with zeros on the rest (D5),
    needs a net P&L per event of about (305 / k) x eps_X to reach eps_X per trade date. The weekly
    event members (k about 55-64) need about 5 x eps_X per event; K4-eiafade-01 (k about 14, a
    passage-based estimate in its entry) needs about 20 x (section 7, item 4).
- **C12 Release-minute cost.** D8's five calibration dates are all Wednesdays, so crude's 09:30
  bucket contains the WPSR on every date (conservative for crude members). The Thursday gas-storage
  release never appears in the sample, so the gas vehicle's 09:30 bucket is calibrated on
  non-release minutes and may understate K4-ngrev-01's and K4-ngpre-01's release-window cost
  (section 7, item 5).
- **C13 Price-limit proximity (D9.7) for NYMEX energy.**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  - **Premise:** these products carry dynamic circuit breakers rather than fixed daily price limits
    (lead's brief; not verified in E.0).
  - **What E.2 must do:**
    - (a) Read CME's NYMEX price-fluctuation and circuit-breaker rules for CL, QM, MCL, NG, QG, MNG,
      RB and HO as they stood over 2019-2026.
    - (b) Decide, with the user, whether Topstep's "Holding a position within 2% of a product's
      price lock limit" [F2.1] applies to a dynamic band. If it does, encode it as D9.7 does: no
      entry, and an immediate exit, while the price is within 2% of the band edge.
    - (c) Confirm that halts produce missing bars, which C4 handles.
  - **Assumption:** the catalog assumes no limit either way.

---

## 1. Members

### K4-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K4. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures and admissible contracts** (each a separate trial): crude {CL, QM, MCL}, gas
  {NG, QG, MNG}, RBOB {RB}, ULSD {HO}. Each is traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1
  log A10 and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the
    trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open),
    in the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or
    after C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else
    no trade."
  - **K4 log:** K4-037 (USO: the first half-hour return, mostly its overnight part, predicts the last
    half-hour, P-K4-037-a) is this mechanism on a crude vehicle and is recorded as **covered by
    CP1**. K5-028's same-day continuation for oil (P-K5-028-a [K4]) is in the same family (section
    5).
- **Instantiated with the D6 energy row (O = 08:00, C = 13:30, F = 15:08):**
  - **Signal:** close of the bar at 08:29 minus the open of the trade date's first bar (the 17:00 CT
    bar of d-1, C3).
  - **Entry:** market intent on the bar at 12:59, filling at the 13:00 open.
  - **Exit:** market intent on the first bar at or after 13:28, filling nominally at the 13:29 open.
  - **Holding horizon:** 29 minutes. **Session window:** 13:00-13:29 CT. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid, with history
  2019-05..2026-06 (micros shorter, C8). The latest signal input, the 08:29 bar, is available at
  08:30 CT.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (C6).
- **Parameters:** O+29 = 08:29, C-31 = 12:59, C-2 = 13:28 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes.
  Floor: at most 20 entries a day, ok; 2-minute minimum hold, ok; 10-minute mean hold, ok.
- **Falsification:** the standard condition only (a port; D6 is unchanged). UCB95 of the member's
  mean net daily P&L per contract below eps_X, at >= 80% achieved null power on the confirmation
  window, counts against it.
- **Topstep check:**
  1. Flat by F: last fill 13:29.
  2. Order type: market.
  3. D9.4: one trade a day, no stops, brackets or passive fills.
  4. *: MCL is starred with its restriction unresolved (D9.8). This applies only if D2 picks MCL
     for crude.
  5. News: 1 lot-equivalent, half the 2-lot maximum. On scheduled FOMC days the entry fill (13:00)
     falls in the statement minute (Topstep F6 "FOMC Statement | 1:00 PM | All products"). That is
     allowed at 1 lot-equivalent, but noted in section 7, item 3.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of each admitted K4 vehicle, research window 2025-04-01..2026-06-19 and
  confirmation S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K4-cp2-01 (core port CP2, opening-range breakout)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-07: the buffer is 4 ticks of the exposure's MOST ACTIVE contract, per D6: crude 0.04 on CL, QM and MCL alike; natural gas 0.004 on NG, QG and MNG alike. The per-vehicle buffer table below is superseded.]
- **Cluster** K4. **Products read:** own vehicle.
- **Exposures:** crude, gas, RBOB, ULSD, one trial each. Each is traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py,
  hold_minutes = 75), as fixed in D6 row CP2 with the 21:12 amendment.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first
    bar opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P;
    market intent in the break direction; one entry per trade date; no entry from C on. Exit: 75
    minutes after the fill, or the engine's forced flatten at F if earlier."
  - **K4 log:** K4-013 (Holmberg, Lönnbark and Lundström, an opening-range breakout on WTI crude
    futures; D.1 B4) is this family on crude and is recorded as **covered by CP2**. K4-043's stop-order
    fact (CL has the highest stop-order share of the three markets studied, P-K4-043-b) is the
    family's microstructure background. K4-050, a pre-registered ORB-cost study, is blocked at title
    only.
- **Instantiated:**
  - **Opening range:** the bars opening in [08:00, 08:15).
  - **Eligible bars:** those opening in [08:15, 13:30). No entry from 13:30 CT on.
  - **Buffer, 4 ticks of the vehicle (C7):**

    | Vehicle | Buffer | Per contract |
    |---|---|---|
    | CL | 0.04 | $40 |
    | QM | 0.100 | $50 |
    | MCL | 0.04 | $4 |
    | NG | 0.004 | $40 |
    | QG | 0.020 | $50 |
    | MNG | 0.004 | $4 |
    | RB | 0.0004 | $16.80 |
    | HO | 0.0004 | $16.80 |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is
    <= OR_low - buffer sells. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it. The exit intent is
    emitted on the 75th bar after the entry-intent bar and fills at the next open. The engine's
    flatten at F is the backstop.
  - **Holding horizon:** 75 minutes. The latest entry fill is 13:30 and its exit 14:45, so F never
    binds on a full session. **Session window:** 08:16 to 14:45 at the latest.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known
  at 08:15 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks, hold 75 minutes (D6, a literal port). **Grid:**
  none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: latest exit 14:45.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. *: MCL flag, as in CP1.
  5. News: 1 lot-equivalent. A position may be open at the 09:30 WPSR or storage release or at the
     13:00 FOMC statement, which F6.3 allows below full maximum size.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K4-cp3-01 (core port CP3, prior-close location)
- **Cluster** K4. **Products read:** own vehicle.
- **Exposures:** crude, gas, RBOB, ULSD. Each is traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L
    over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as
    Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells,
    market intent on the O bar of day d. Exit: first bar at or after C-2 min."
  - **K4 log:** K5-028's next-day momentum for oil (P-K5-028-a [K4]) is a prior-day follow-through
    in this family (section 5).
- **Instantiated:**
  - **Daily bar:** O_d = open of the 08:00 bar. H and L are taken over the bars opening in
    [08:00, 13:30). C_d = close of the 13:29 bar.
  - **Complete day** (Family H): the 08:00 and 13:29 bars exist, the date is not an early halt, and
    every bar in [08:00, 13:30) carries one instrument_id.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of day d's 08:00 bar.
  - **CLV:** computed in ticks, with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells
    (non-strict, as H6).
  - **Entry:** market intent on the 08:00 bar of d, filling at the 08:01 open.
  - **Exit:** first bar at or after 13:28, filling nominally at the 13:29 open.
  - **Holding horizon:** about 328 minutes. **Session window:** 08:01-13:29.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's
  bar is complete at 13:30 CT on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 328 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:29.
  2. Order type: market.
  3. D9.4: ok.
  4. *: MCL flag.
  5. News: holds through the Wednesday WPSR, the Thursday storage report and FOMC statements at 1
     lot-equivalent, which is not the full maximum (D9.5).
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K4-ngpre-01 (natural gas storage-report day: short from 90 minutes before to 30 minutes after)
- **Cluster** K4. **Products read:** the gas vehicle; EC-NGS; EC-CAL.
- **Traded exposure:** Henry Hub gas {NG, QG, MNG}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** NG futures earn a negative average return on EIA storage-report days.
    "The entire effect (99%) stems from the two hour window surrounding the announcement"
    (P-K4-001-b). The return splits half before and half after the release (P-K4-001-a). The
    (-90, 30) window averages -0.37% (p 0.000) (P-K4-001-c). "Opening a short position 90 minutes
    before the announcement and closing it 30 minutes afterwards" is the authors' own strategy
    (P-K4-001-d).
  - **Evidence against, from the same source:** after 2011 the strategy is flat to negative after
    costs: "Raw + TC + FC -0.97 (0.843)" (P-K4-001-e). Its Sharpe ratios are annualized with 252 on
    a weekly trade (P-K4-001-f). The confirmation window (2019-2024) lies wholly after 2011, so the
    expected outcome is null. The member tests whether the puzzle is absent in 2019-2026 at the
    funnel's bar.
  - **Classification:** port of D.1 family E (pre-release window), gas-specific. D6 does not port
    family E, so this is a cluster member (new to Stage E).
- **Event set:** every EC-NGS release that passes C9's checks. The release time T (CT) is 09:30 in
  the standard slot, 11:00 for the Wednesday or Monday 12:00 ET exceptions, and 09:30 for the Friday
  10:30 ET exceptions.
- **Entry rule:** SELL, market intent on the bar at T - 91 min, filling at the open of T - 90
  (standard: intent on the 07:59 bar, fill at the 08:00 open).
- **Exit rule:** market intent on the bar at T + 29, filling at the open of T + 30 (standard 10:00).
- **Holding horizon:** 120 minutes. **Session window:** 08:00-10:00 CT (standard); 09:30-11:30 CT
  for 11:00 CT releases. Flat by F (latest fill 11:30).
- **Data fields read:**
  - Vehicle ohlcv-1m open and instrument_id (C8). Paid, 2019-05..2026-06 (MNG from 2023-11, C8).
  - EC-NGS release date and time. Free, with 2019-2026 history (C9). Known before d.
  - EC-CAL. Known in advance.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** entry at T - 90 and exit at T + 30 (P-K4-001-c, P-K4-001-d); side SELL (the
  window's average return is negative, P-K4-001-c). **Grid:** none.
- **Expected entries and hold:** one per release. That is about 64 in the research window and about
  252 in the confirmation window, before C4's exclusions and S_X (C11): about 0.2 per trade date,
  held 120 minutes. Floor ok.
- **Falsification:**
  - The standard condition (UCB95 of mean net daily P&L per contract below eps_X at >= 80% achieved
    null power on the confirmation window counts against it).
  - **Sign check, reported beside the verdict and not a separate test:** the mechanism predicts a
    negative mean gross move of the vehicle, in ticks, from the T - 90 open to the T + 30 open on
    event days. A non-negative confirmation-window mean counts against the mechanism.
- **Topstep check:**
  1. Flat by F: latest fill 11:30.
  2. Order type: market.
  3. D9.4: one trade per release, no stops. Entry 90 minutes before the release, not in a gapped
     market.
  4. *: none (NG, QG, MNG unstarred).
  5. News: holds into the storage release ("Natural Gas Inventories (EIA) | 9:30 AM | NG, QG";
     "**Micro contracts also apply", F6) at 1 lot-equivalent, which F6.3 and D9.5 allow.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the gas vehicle (research and confirmation windows); external EC-NGS
  and EC-CAL.
- **Trials in N:** 1.

### K4-ngrev-01 (natural gas storage-report response reversal, week to week)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-06: EXCLUDED. Its own source's abstract (K4-006) says "Analyst's natural gas forecasts efficiently impound the available time-series information", which contradicts step 2 (the surprise reversal) the member rests on. 0 trials. The entry is kept below for the record only.]
- **Cluster** K4. **Products read:** the gas vehicle; EC-NGS; EC-CAL.
- **Traded exposure:** Henry Hub gas {NG, QG, MNG}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "Storage flows higher or lower than analysts had expected one week tend to
    be partially reversed the following week" (K4-006 P-K4-006-a, abstract only).
  - **The rule-3 route.** The surprise itself needs the proprietary consensus, so it is observed
    through the price response. That is the route rule 3 names: "the first minutes' price response
    as the surprise". The reasoning, step by step:
    1. The release response is inverse to the storage surprise. P-K4-002-d: "an unexpected 1%
       increase in natural gas in storage results in a 2.4% drop in natural gas futures prices".
       P-K4-028-a: "an inverse empirical relation between changes in futures prices and surprises".
       So the sign of last week's surprise is minus the sign of last week's release response
       R_{k-1}.
    2. By P-K4-006-a, this week's surprise tends to have the opposite sign of last week's.
    3. So this week's release response R_k tends to have the opposite sign of R_{k-1}. The position
       is -sign(R_{k-1}), held across this week's release in the event window P-K4-002-b fixes
       ("from five minutes before to ten minutes after the announcement time").
  - **Open questions:**
    - Step 2 rests on an abstract.
    - Whether the market already prices the reversal is [unverified]. The same abstract says "the
      market promptly incorporates analyst forecasts into oil and gas prices prior to the EIA
      announcements".
    - Whether the reversal also holds for crude is not stated. The sentence sits in the natural-gas
      part of the abstract, so the member is written for gas only.
  - **Classification:** new to the program (K4-006's log tag: "week-to-week surprise reversal as a
    predictor of the next surprise").
- **Event set:** release k in EC-NGS at T_k, with release k-1 the immediately preceding EC-NGS
  entry at T_{k-1}. Both pass C9's checks.
- **Signal:** R_{k-1} = close of the vehicle's bar at T_{k-1} + 9 minus close of its bar at
  T_{k-1} - 1, in ticks. Both bars must exist with one instrument_id; they need not match release
  k's contract, since only the sign is used. R_{k-1} = 0 means no trade.
- **Entry rule:** market intent on the bar at T_k - 6, filling at the open of T_k - 5 (standard:
  09:25). BUY if R_{k-1} < 0; SELL if R_{k-1} > 0.
- **Exit rule:** market intent on the bar at T_k + 9, filling at the open of T_k + 10 (standard:
  09:40).
- **Holding horizon:** 15 minutes. **Session window:** 09:25-09:40 CT (standard); 10:55-11:10 CT for
  11:00 CT releases. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close, open and instrument_id on release k-1's date and on release k's date
    (C8).
  - EC-NGS and EC-CAL (C9).
  - The signal is available at T_{k-1} + 10, about a week before the entry.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - The signal window, from T - 1 to T + 9 bar closes, is the post-release part of P-K4-002-b's
    window.
  - The trade window, from T - 5 to T + 10, is P-K4-002-b's window.
  - Direction: -sign(R_{k-1}), from P-K4-006-a with P-K4-002-d.
  - **Grid:** none.
- **Expected entries and hold:** about one per week: about 64 research and 252 confirmation events,
  before exclusions and R_{k-1} = 0 cases. Held 15 minutes. Floor ok: the 2-minute minimum and the
  10-minute mean both hold.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of direction x (open at T_k + 10 - open at T_k - 5), in
    ticks, is positive.
  - **Reported beside it:** the correlation of consecutive responses (R_{k-1}, R_k) over the
    window's releases, which the mechanism predicts is negative.
- **Topstep check:**
  1. Flat by F: latest fill 11:10.
  2. Order type: market.
  3. D9.4: one trade per release. It enters 5 minutes before the release and exits 10 minutes
     after, so neither fill is in the release minute. Slippage is charged at the 09:30 bucket (C12).
  4. *: none.
  5. News: holds through the storage release at 1 lot-equivalent (F6.3).
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the gas vehicle; external EC-NGS, EC-CAL.
- **Trials in N:** 1.

### K4-apipre-01 (API-to-EIA continuation before the crude inventory release)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP until E.1 records its source windows (K4-022, K4-023).]
- **Cluster** K4. **Products read:** the crude vehicle; EC-WPSR; EC-API (timing rule only); EC-CAL.
- **Traded exposure:** WTI crude {CL, QM, MCL}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "This inefficiency can be exploited by sophisticated traders. ... We also
    construct a predictor that can predict inventory surprises and pre-announcement returns
    in-sample and out-of-sample" (K4-009 P-K4-009-a, abstract). The log's reading of that abstract:
    the API bulletin is informative about the next day's WPSR, yet CL does not fully absorb it.
  - **The rule-3 route.** The API bulletin is proprietary, so its content is observed through CL's
    response in the API window. API crude-inventory shocks move 15-minute CL returns (P-K4-023-b:
    positive and negative shock coefficients -0.134 and -0.126). The API is released "Tuesdays at
    4:30pm EST" (P-K4-023-a; P-K4-045-a), that is, about 15:30 CT. The sign of that response is the
    market's reading of the API news. Under incomplete absorption, the pre-release return continues
    in the same direction.
  - **Pre-release window:** informed selling and a price run-up begin "around 08:30 ET, two hours
    before the 10:30 release" (log mechanism line for K4-022; verbatim: P-K4-022-b "ahead of the
    EIA-DOE inventory release each Wednesday" and P-K4-022-e "the average OID over the 8:30 – 9:30
    period"). 08:30 ET = 07:30 CT.
  - **Supporting:** K4-026 P-K4-026-c ("the futures market seems to anticipate the surprises
    correctly one day before") and K4-046 P-K4-046-a (practitioner claim, untested).
  - **Classification:** new to the program (API-to-EIA sequential information).
- **Event set:** EC-API standard weeks (C9). The WPSR is on its Wednesday 09:30 CT slot, and the
  preceding Tuesday is a full-session trade date.
- **Signal:** R_API = close of the vehicle's bar at 15:39 CT on the Tuesday minus close of its bar
  at 15:24 CT on the Tuesday, in ticks. That is the (-5, +10)-minute window around 15:30 CT, the
  convention of P-K4-002-b applied to the API time. Both bars must exist with one instrument_id.
  R_API = 0 means no trade.
- **Entry rule:** Wednesday, market intent on the bar at 07:29, filling at the 07:30 open, in the
  direction sign(R_API).
- **Exit rule:** market intent on the bar at 09:28, filling at the 09:29 open. The member is flat
  before the 09:30 release.
- **Holding horizon:** 119 minutes. **Session window:** 07:30-09:29 CT. Flat by F.
- **Why the exit precedes the release:**
  - The verified claim is about "pre-announcement returns" (P-K4-009-a).
  - The release response is contemporaneous (K4-002).
  - A fill in the release minute is the gapped-market case D9.4 warns about.
  - The through-release variant is not written (section 3).
- **Data fields read:**
  - Vehicle ohlcv-1m close, open and instrument_id: on the Tuesday at 15:24 and 15:39 (Globex,
    after the 13:30 settlement; available by 15:40 CT on the Tuesday), and on the Wednesday 07:29 to
    09:29 (C8).
  - EC-WPSR, EC-API rule, EC-CAL (C9), all known before the Tuesday.
  - The API bulletin itself is never read.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - Signal bars 15:24 and 15:39 (P-K4-045-a time with P-K4-002-b's -5/+10 window).
  - Entry 07:30 (P-K4-022-b, P-K4-022-e).
  - Exit 1 minute before T_W.
  - **Grid:** none.
- **Expected entries and hold:** about 56 standard weeks in the research window and about 210 in the
  confirmation window (C11), before exclusions and R_API = 0 days. That is about 0.18 per trade
  date, held 119 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(R_API) x (open at 09:29 - open at 07:30), in ticks,
    on event days is positive.
- **Topstep check:**
  1. Flat by F: last fill 09:29.
  2. Order type: market.
  3. D9.4: one trade a week, no stops, no fill near the release.
  4. *: MCL flag (crude).
  5. News: flat before the 09:30 WPSR ("Crude Oil Inventories (EIA) | 9:30 AM / 10:00 AM* | CL, QM,
     MCL, RB", F6). 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Member-level coverage (D9):** E.2's coverage check must cover the entry window (07:30-09:29)
  and the two Tuesday signal minutes, which fall after the settlement.
- **Data needed:** ohlcv-1m of the crude vehicle, including the post-settlement Tuesday minutes;
  external EC-WPSR, EC-API rule, EC-CAL.
- **Trials in N:** 1.

### K4-eiafade-01 (post-WPSR overreaction fade)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP until E.1 records its source window (K4-022 body not retrieved).]
- **Cluster** K4. **Products read:** the crude vehicle; EC-WPSR; EC-CAL.
- **Traded exposure:** WTI crude {CL, QM, MCL}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** CL overreacts to the WPSR and partly reverses over the following hours: "an
    over-reaction that is partly compensated in the hours following the announcement" (P-K4-022-a).
    On positive-surprise days the release brings "a large average price drop of about 0.5% ...
    partly corrected in the hours following the news release. Four hours later, the drop is half as
    large, i.e. 0.25%" (P-K4-022-d).
  - **The rule-3 route.** The source conditions on 3-sigma Bloomberg surprises (P-K4-022-c), which
    are proprietary. The proxy is the first 15 minutes' price response (rule 3), with the source's
    own average release move as the threshold for a large response.
  - **Symmetric:** P-K4-022-a's over-reaction statement is not restricted to positive surprises. The
    0.5% magnitude comes from positive-surprise days (P-K4-022-d). The reversal after large price
    rises is [unverified in the logged passages].
  - **Classification:** port of D.1 family C (reversal after an event shock) conditioned on family E
    (log tag). New member.
- **Event set:** every EC-WPSR release that passes C9's checks with T_W + 15 <= 13:13 CT, so the
  entry precedes the exit by at least 15 minutes. That covers the 09:30, 10:00 and 11:00 CT slots
  and excludes the 16:00 CT Monday release.
- **Signal:** M = (close of the bar at T_W + 14 - close of the bar at T_W - 1) / close of the bar at
  T_W - 1 (C10: the denominator must be > 0). Both bars must exist with one instrument_id.
- **Entry rule:**
  - If M <= -0.005: BUY.
  - If M >= +0.005: SELL.
  - Otherwise no trade.
  - Market intent on the bar at T_W + 14, filling at the open of T_W + 15 (standard 09:45).
- **Exit rule:** market intent on the first bar at or after 13:28, filling nominally at the 13:29
  open. This is the ports' C-2 convention. For the standard 09:30 release it ends the position at
  the end of P-K4-022-d's "Four hours later" horizon (13:30 CT).
- **Holding horizon:** 224 minutes (standard); 194 for 10:00 CT releases; 134 for 11:00 CT
  releases. **Session window:** 09:45-13:29 CT (standard). Flat by F.
- **Data fields read:** vehicle ohlcv-1m close, open and instrument_id (C8), available at the close
  of the bar at T_W + 14; EC-WPSR and EC-CAL (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Measurement window of 15 minutes after the release: a judgment.** It matches the 15-minute
    windows of the log's intraday release studies: P-K4-033-a "During the 15 minutes following
    supply announcements"; K4-023's 15-minute API and EIA windows (P-K4-023-a, P-K4-023-b); and
    P-K4-002-b's +10 minutes, rounded up to the next quarter hour.
  - **Threshold 0.5% of price:** P-K4-022-d.
  - **Exit at C - 2:** P-K4-022-d's four-hour horizon.
  - **Grid:** none.
- **Expected entries and hold:**
  - About 63 eligible releases in the research window and about 250 in the confirmation window.
  - Trades only on large responses. The passages suggest roughly one release in four or five
    qualifies: "90 surprises (22.39%)" of 402 (P-K4-022-c) and "11 out of 50 EIA reports generated
    significant return jumps" (P-K4-023-c). That gives about 14 research and about 55 confirmation
    trades.
  - This is a passage-based expectation, not a price-data estimate.
  - Holds 134-224 minutes. Floor ok.
  - Power: probably "inconclusive by design" under D4 (section 7, item 4).
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of -sign(M) x (open at 13:29 - open at T_W + 15), in ticks,
    on traded days is positive. It is also reported split by the sign of M, since the evidence is
    for price drops.
- **Topstep check:**
  1. Flat by F: last fill 13:29.
  2. Order type: market.
  3. D9.4: one trade per release. It enters 15 minutes after the release, not in the release minute
     or the gapped first minutes.
  4. *: MCL flag.
  5. News: the position starts after the release. 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the crude vehicle; external EC-WPSR, EC-CAL.
- **Trials in N:** 1.

### K4-eiamom-01 (WPSR-day release half-hour predicts the last NYSE half-hour)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP until E.1 records its source window (K4-021 body not retrieved).]
- **Cluster** K4. **Products read:** the crude vehicle; EC-WPSR; EC-NYSE; EC-CAL.
- **Traded exposure:** WTI crude {CL, QM, MCL}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "returns on the third half-hour on EIA announcement days can significantly
    and positively predict the returns in the last half-hour" (K4-021 P-K4-021-a). The EIA-day
    slope is 0.038 (t 2.12), with adjusted R2 3.10% over 591 Wednesday 10:30 ET releases
    (P-K4-021-c).
  - **The source's instrument and clock:** USO, on 1-minute data (P-K4-021-b). The half-hours are
    NYSE half-hours, 09:30-16:00 ET (log product line). The third half-hour is 10:30-11:00 ET, the
    release interval; the last is 15:30-16:00 ET.
  - **Transfer to CL (reasoning, untested by the source; log quality tell 1).** USO holds CL futures
    and its intraday price tracks them. A USO half-hour return is therefore a crude-futures return
    over the same clock interval, up to tracking error. Both half-hours are traded on the same
    clock: 09:30-10:00 CT and 14:30-15:00 CT. 14:30-15:00 CT falls after the 13:30 CL settlement,
    but inside the XFA day.
  - **Counter-evidence:**
    - P-K4-037-b: "the information contained in the inventory announcements does not offer
      predictability to the last half-hour returns" (same first author, 2006-2018).
    - P-K4-021-e: a declining trend, and no predictability in 2014-2016.
    - No costs in the source (log quality tell 3).
  - **Classification:** port of D.1 family C (intraday momentum) conditioned on family E (log tag).
    It differs from CP1 in its signal half-hour, event days and traded window. New member.
- **Event set:** standard WPSR Wednesdays (T_W = 09:30 CT, not in the exception table, the source's
  "Wednesday-10:30" sample). The date must be a full session in both EC-CAL and EC-NYSE.
- **Signal:** r3 = close of the bar at 09:59 minus close of the bar at 09:29, that is, the price at
  11:00 ET minus the price at 10:30 ET, in ticks. Both bars must exist with one instrument_id.
  r3 = 0 means no trade.
- **Entry rule:** market intent on the bar at 14:29, filling at the 14:30 open (15:30 ET), in the
  direction sign(r3).
- **Exit rule:** market intent on the first bar at or after 14:58, filling nominally at the 14:59
  open. This is CP1's C-2 convention with C = 15:00 CT, the NYSE close.
- **Holding horizon:** 29 minutes. **Session window:** 14:30-14:59 CT, flat 9 minutes before F.
- **Data fields read:** vehicle ohlcv-1m close, open and instrument_id (C8), with the signal
  available at 10:00 CT; EC-WPSR, EC-NYSE and EC-CAL (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** signal bars 09:29 and 09:59, the third NYSE half-hour (P-K4-021-a; log product
  line); trade window 14:30-14:59, the last NYSE half-hour. **Grid:** none.
- **Expected entries and hold:** about 56 research and about 210 confirmation events before
  exclusions (C11): about 0.18 per trade date, held 29 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(r3) x (open at 14:59 - open at 14:30), in ticks, on
    event days is positive.
  - **Descriptive control (not a trial):** the same statistic on full-session Tuesdays, Thursdays
    and Fridays. There, P-K4-021-a says r3 has no predictive power.
- **Topstep check:**
  1. Flat by F: last fill 14:59, 9 minutes before F.
  2. Order type: market.
  3. D9.4: one trade a week, no stops.
  4. *: MCL flag.
  5. News: no scheduled K4 release in the window. 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Member-level coverage (D9):** the window lies after the 13:30 settlement. E.2's coverage check
  decides whether it can be screened.
- **Data needed:** ohlcv-1m of the crude vehicle; external EC-WPSR, EC-NYSE (to be sourced in E.2),
  EC-CAL.
- **Trials in N:** 1.

### K4-ovr-01 (hourly overreaction reversal)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source sample is 2019-11-20 to 2020-06-03, inside the confirmation window, and its crude figure is driven by the 2020-04-20 negative-price episode (review R-16).]
- **Cluster** K4. **Products read:** each traded exposure's own vehicle; EC-CAL.
- **Traded exposures** (each a separate trial): crude {CL, QM, MCL}, ULSD {HO}, gas {NG, QG, MNG}.
  These are the K4 products in the source's sample: "WTI crude oil (CL), Brent crude oil (CO),
  heating oil (HO), natural gas (NG)" (P-K5-029-b [K4]). RBOB is not in the sample and is not
  traded. Each exposure is traded only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed** (K5-029, a panel source; the [K4] passages are in the K5 log): large
    intraday price changes beyond a decile threshold, at 1-minute to 1-hour frequencies, are
    followed by reversals in commodity futures. "Soft and metal commodities show much less
    overreactions than precious metals and especially energy commodities" (P-K5-029-a).
  - **Crude result:** "An investor who would have traded all crude oil long positions after the
    10% highest negative price changes, would have also traded this price reversal and consequently
    would have realized a trading return of 11.91%" (P-K5-029-c [K4]).
  - **Costs:** net results are asserted positive "for positive and negative initial price changes"
    (P-K5-029-d).
  - **Evidence quality:** about six months of data (2019-11-20 to 2020-06-03, Covid-dominated,
    P-K5-029-a); costs asserted, not modelled; holding period [unverified] (K5 log quality tells).
  - **Classification:** a family C magnitude-conditioned reversal, tested on energy products
    specifically. D6 does not port family C, so under partition rule 6 this is a cluster member.
- **Decision times:** t in {09:00, 10:00, 11:00, 12:00, 13:00} CT, the five whole hours of the
  energy day session from O = 08:00.
- **Signal:** r(t) = (close of the bar at t - 1 - open of the bar at t - 60) / open of the bar at
  t - 60. The denominator must be > 0 (C10), and both bars must exist with one instrument_id.
- **Reference set and cuts:**
  - The reference set is the values r(tau) at the same five clock times on the 20 most recent
    earlier trade dates that are full sessions in EC-CAL. Every value whose two bars exist with one
    instrument_id counts, and at least 80 values are required, else no trade at t.
  - P10 and P90 = np.percentile(values, [10, 90], method="linear").
  - Warm-up: the first 20 eligible dates of each window. No bars before the research window exist:
    holdout-2 is sealed.
- **Entry rule:**
  - r(t) <= P10: BUY.
  - r(t) >= P90: SELL.
  - Otherwise no trade.
  - Market intent on the bar at t - 1, filling at the open of the bar at t.
- **Exit rule:** market intent on the bar at t + 58, filling at the open of t + 59. At most one
  position is open. The next decision's entry fills at t + 60, so positions never overlap.
- **Holding horizon:** 59 minutes. **Session window:** 09:00-13:59 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8), all closed at or before
  t; EC-CAL.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **60-minute signal and decile cuts:** the source's 1-hour frequency and "10% highest negative
    price changes" (P-K5-029-c). The symmetric upper cut follows P-K5-029-d.
  - **20-trade-date trailing reference: a judgment.** It is the program's trailing-state length
    (D15.4 B4). The source's own threshold construction is not in the logged passages.
  - **59-minute hold: a judgment.** It is one signal period less the one-minute gap that keeps
    positions from overlapping. The source's holding period is [unverified].
  - **Grid:** none.
- **Expected entries and hold:** by construction about 2 in 10 decision times qualify if the trailing
  distribution is stable. That is about 1 entry per day per exposure (at most 5), held 59 minutes.
  Floor ok.
- **Falsification:**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of -sign(r(t)) x (open at t + 59 - open at t), in ticks, is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: at most 5 entries a day, each held 59 minutes, no stops or brackets. Not scalping.
  4. *: MCL flag for crude.
  5. News: the 10:00 decision on release days reads an hour containing the 09:30 release and may
     fade it at 10:00, 30 minutes after the release. 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the crude, ULSD and gas vehicles (research and confirmation windows).
- **Trials in N:** 1 per admitted exposure among crude, ULSD and gas (at most 3).

### K4-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 ADV order): WTI crude, natural gas, RBOB, ULSD; if none is admitted, no ML member. Features unchanged.]
- **Traded vehicle: WTI crude exposure** {CL, QM, MCL}; the contract is chosen by D2 in E.2.
  - **Reason:** crude is the K4 exposure the log documents most often at intraday horizons:
    K4-002, 003, 007, 009, 020, 021, 022, 023, 025, 026, 032, 033, 037, 043, 044 and 046, against
    nine gas items (K4-001, 004, 005, 006, 012, 028, 029, 031, 038). It also has the cluster's
    highest public ADV: CL 1,079,857 contracts per day, 2026 Jan-Aug (design D1 table).
  - **No fallback is declared.** The cluster features below are crude-specific (API and WPSR
    timing), so they would not transfer to another exposure. If D2 admits no crude contract, the
    lead decides.
  - **MCL flag:** if D2 picks MCL, the unresolved * restriction applies (D9.8).
- **Products the features read:**
  - The crude vehicle.
  - RB bars, needed as a leg even if RBOB is not traded. D13 buys history only for the chosen
    vehicle of each traded exposure, so E.2 must add RB's history if RBOB is not admitted.
  - Calendars: EC-WPSR, EC-NGS, EC-CAL, and the EC-API timing rule.
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12. Throughout, t_j is the
  decision time, "the bar at t_j - 1" is the last bar closed at t_j, and tick is the vehicle's tick.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | wpsr_phase | If d carries a WPSR release at T_W (EC-WPSR): -1 if T_W - 120 min <= t_j < T_W; +1 if T_W <= t_j < T_W + 240 min; else 0. If d carries no release: 0 | K4-017 P-K4-017-a, P-K4-017-b (schedule); K4-022 P-K4-022-b, P-K4-022-e (pre-release window from 08:30 ET), P-K4-022-d ("Four hours later") | schedule known before d (C9); depends only on the clock |
| KF2 | wpsr_move | If d carries a WPSR release at T_W and t_j >= T_W + 15: (close of the bar at T_W + 14 - close of the bar at T_W - 1) / tick; else 0. On such a d with t_j >= T_W + 15, a missing bar or a change of instrument_id means no trade at t_j | K4-022 P-K4-022-a, P-K4-022-d; K4-023 P-K4-023-b, P-K4-023-c; K4-002 P-K4-002-b; K4-033 P-K4-033-a (15 minutes); K4-021 P-K4-021-a | T_W + 15 (close of the bar at T_W + 14) |
| KF3 | api_move | If d is an EC-API standard-week Wednesday (C9): (close of the bar at 15:39 CT - close of the bar at 15:24 CT, both on the previous calendar day) / tick; else 0. On such a d, a missing bar or a change of instrument_id means no trade at any t_j of d | K4-009 P-K4-009-a; K4-023 P-K4-023-a, P-K4-023-b; K4-045 P-K4-045-a; K4-046 P-K4-046-a | 15:40 CT on d-1, before d's first decision |
| KF4 | ngs_phase | If d carries a storage release at T_N (EC-NGS): -1 if T_N - 90 min <= t_j < T_N; +1 if T_N <= t_j < T_N + 30 min; else 0. If d carries no release: 0 | K4-018 P-K4-018-a (schedule); K4-002 P-K4-002-e (the gas report moves crude: "Crude Oil -0.14 (0.08)*"); K4-001 P-K4-001-c (the (-90, 30) window) | schedule known before d |
| KF5 | rb_ret30 | (close of the RB bar at t_j - 1 - open of the RB bar at t_j - 30) / 0.0001, in RB ticks. Both bars must exist with one RB instrument_id, else no trade at t_j | K4-020 P-K4-020-a, P-K4-020-d ("the change in gasoline futures price has a significantly greater impact on WTI crude oil futures price than in the opposite case") | RB bar closes <= t_j |
| KF6 | gsci_roll | 1 if d is the 5th, 6th, 7th, 8th or 9th trade date of its calendar month in EC-CAL; else 0. The index's own business-day calendar is not logged, so it is approximated by energy trade dates, a judgment | K4-034 P-K4-034-b ("from the fifth to the ninth business day ... 20% of its positions"); K4-036 P-K4-036-c; K4-003 P-K4-003-c, P-K4-003-d | calendar known in advance |
| KF7 | ret60_pct | Let r60(tau) = (close of the vehicle's bar at tau - 1 - open of its bar at tau - 60) / tick. The value is (number of reference values < r60(t_j) + 0.5 x number equal) / (number of reference values). The reference set is r60 at the 15 decision clock times on the 20 most recent earlier eligible trade dates, counting each value whose bars exist with one instrument_id; at least 240 values are required, else no trade at t_j | K5-029 P-K5-029-a, P-K5-029-c [K4] (decile overreactions at the 1-hour frequency, strongest in energy), P-K5-029-d | bars closed <= t_j, and earlier trade dates |

- **Decision window [W0, W1] = [07:15, 14:15] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 07:15, 07:45, ..., 14:15, which is 15 a day. W1 + h = 14:45 <= F.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 to the open of t_j + 30.
    Every fill therefore falls at :16, :46, :15 or :45.
  - **Why this window:** it starts before K4-022's informed pre-release window, which opens about
    07:30 CT (P-K4-022-b, P-K4-022-e). The :15 offset puts every scheduled K4 event minute strictly
    inside a position interval and never at a fill:
    - the 09:30 WPSR and storage releases (inside [09:16, 09:45]);
    - the 10:00 and 11:00 CT holiday release slots;
    - the London Trading-at-Marker minute, 16:29-16:30 London time (P-K4-047-a), which is 10:29 CT
      for most of the year and 11:29 CT in the weeks when UK and US clock changes differ;
    - the 13:00 CT FOMC statement;
    - the 13:28-13:30 CT settlement window (K4-003's "14:28-14:30 ET").

    No ML fill lands in a release minute, the gapped-market case of D9.4.
  - **Why h = 30:** it is the horizon over which the logged responses play out:
    - K4-021's half-hour structure (P-K4-021-a);
    - the +30-minute end of K4-001's report window (P-K4-001-c);
    - "volatility up to 30 minutes following the announcement was also higher than normal"
      (P-K4-004-a).

    h = 15 would sit inside the release spike and its 15-minute response windows (K4-002, K4-023).
    h = 60 or 120 would fold the release, the TAM marker and the post-release reversal into one
    interval.
- **Expected rows:** about 15 x the eligible research-window trade dates. That is about 305 trade
  dates, less roll-blackout, vendor-degraded and early-halt dates (D15.3), and less the 20-date
  warm-up of KF7 and B4: roughly 3,700-4,200 rows. E.2 gives the exact count.
- **Expected entries:** at most 15 per day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it). Failing the D5 screen
  puts it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 14:45.
  2. Order type: market (D15.6).
  3. D9.4: at most 15 entries a day, 30-minute holds, no stops or brackets. No fill in a release
     minute.
  4. *: MCL flag.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span a release.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:**
  - ohlcv-1m of the crude vehicle and RB. The research window is used for training and tuning, the
    confirmation window for the frozen model.
  - The member-level coverage check covers 07:16-14:45.
  - External: EC-WPSR, EC-NGS, EC-CAL.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K4-ngfcst-01 | NG position before the storage release, signed by the accuracy-weighted analyst predictor: the median forecast of historically accurate analysts minus the consensus (K4-012 P-K4-012-a; K4-005 P-K4-005-a) | Rule 3 (proprietary data) | It needs analyst-level storage forecasts and their accuracy history ("individual forecasts of analysts according to their prior accuracy", P-K4-005-a; Bloomberg per the log). No named, obtainable historical source was found. The crowd alternative (Estimize) is a commercial dataset, and "does not influence the market's expectation ... beyond what is already contained in professional consensus" (K4-031 P-K4-031-a). The obtainable-proxy route to a gas storage predictor is K4-ngrev-01. |
| X-02 K4-surprise-01 | Post-release trade in CL, RB, HO or NG signed by the consensus surprise (K4-002 P-K4-002-a, P-K4-002-d; K4-022 P-K4-022-c; K4-023 P-K4-023-b; K4-028 P-K4-028-a; K4-026 P-K4-026-d) | Rule 3; nothing documented to trade | Consensus surveys (Bloomberg, Reuters) are proprietary, with no named obtainable history. With the price-response proxy, what is documented is contemporaneous: K4-002's -5/+10 window and K4-023's 15-minute windows. NG shows "No evidence ... of economically meaningful reactions to the surprise other than on the date the storage news is released" (P-K4-028-b). The one documented post-release pattern, the partial reversal, is K4-eiafade-01. |
| X-03 K4-ngdisp-01 | NG release reaction conditioned on analyst disagreement (K4-006 P-K4-006-a: "contingent on the level of analyst forecast uncertainty as proxied by analyst forecast disagreement") | Rule 3 | Analyst-level dispersion is proprietary; no obtainable history was named. |
| X-04 K4-anlpub-01 | CL traded on analyst inventory-forecast publications, "prices rise (fall) when analysts forecast a decrease (increase) in supplies" (K4-033 P-K4-033-a) | Rule 3 | Analyst forecasts, their publication times ([unverified] per the log) and the accuracy history the effect depends on are proprietary. |
| X-05 K4-badnews-01 | CL continuation after a bearish WPSR: prices "continue to drift for five minutes when news is negative" (K4-032 P-K4-032-a; abstract only; the event is identified as the WPSR only by the log's reading) | D9.3 floor; D9.4 | A rule that holds only the documented five-minute drift breaks the 10-minute mean-hold floor, D9.3(c). Holding longer to meet it would test an undocumented horizon. The entry would fill in the first minutes after the release, the "reckless trades in gapped markets" case of D9.4 [F7.2], where a bar-open fill cannot represent a real fill. The capturable part after latency is unknown (log tag). |
| X-06 K4-fomcsurp-01 | CL, HO or NG traded on the FOMC target surprise measured from fed funds futures (K4-025 P-K4-025-b, P-K4-025-e; K4-010 P-K4-010-a) | Partition rule 4 (K8); contemporaneous | The surprise is read from a rates instrument, and the channel is the dollar: "Monetary policy affects oil prices mostly by affecting the value of the U.S. dollar" (P-K4-025-a). Energy with rates or the dollar is K8's (section 4). The documented response is contemporaneous (a 1-hour window). For scheduled meetings the intraday crude coefficient is insignificant, "-0.88 (0.8)" (P-K4-010-c, slides). |
| X-07 K4-fomcfade-01 | Fade CL's FOMC-window move into the close (K4-025 P-K4-025-d) | Rule 1 (evidence) | The -0.24 intraday-daily correlation holds "for this specific time series realization", a handful of LSAP events. Scheduled meetings show no significant intraday effect (P-K4-010-c), and scheduled releases do not raise energy jump rates (K4-040 P-K4-040-a). No threshold or window can be traced. |
| X-08 K4-idxroll-01 | Commodity-index roll: short nearby and long deferred CL (or NG, RB, HO) around the GSCI roll ("from the fifth to the ninth business day ... 20% of its positions", P-K4-034-b). Or a single-leg outright short of the nearby into the 13:28-13:30 CT settlement window on roll days (K4-003 P-K4-003-c, P-K4-003-d; K4-036 P-K4-036-c; K4-027 P-K4-027-a) | Flat by F; D2 vehicle; rule 1 | **As documented,** the effect is a nearby-minus-deferred differential over multi-day, settlement-to-settlement windows (P-K4-036-c: 26 bp over the roll window). The front-running strategy holds 1-3 weeks (P-K4-035-b). Both break the 15:08 flat rule. **The spread** is not an exposure's D2 vehicle, and the deferred contract's bars are not in the data plan (D13 buys one vehicle per exposure). **A single-leg intraday version** has no logged passage: the outright nearby's move inside the settlement window is untested. Temporary impact "is reversed within ten minutes" (P-K4-003-b). The pooled roll effect is "17 basis points at most" and "never significant" after standard-error adjustment (P-K4-034-a). Which contract the vehicle holds on roll days depends on E.2's roll convention, which could invert the direction or remove the dates as roll blackout. **What such a member would need:** the S&P GSCI contract schedule per commodity logged (not in the log), E.2's roll convention, and a verified intraday source. **What survives:** the date enters K4-ml-01 as a feature only (gsci_roll). K5 and K6 writers apply the [K5] and [K6] passages to their own products. |
| X-09 K4-tas-01 | Trade alongside large TAS holders' strategic trading around the settlement window (K4-027 P-K4-027-a) | Rule 3 | TAS position concentration is not public; whether any public source exists is [unverified]. The source is an abstract only, and its product coverage is [unverified]. |
| X-10 K4-hogo-01 | HO second contract against ICE Gasoil sixth contract, Ornstein-Uhlenbeck bands (K4-042 P-K4-042-a, P-K4-042-b) | Tradability; flat by F; data | Gasoil is an ICE contract: not Topstep-permitted and not in GLBX.MDP3. Band exits are not bounded by F. The source has one year of data, and its optimal leverage is "too large for practical purposes" (P-K4-042-c). A single-leg HO rule conditioned on the spread would still need ICE bars. |
| X-11 K4-brent-01 | CL traded on a Brent lead, or on the WTI-Brent spread (K4-030 P-K4-030-a; R-K4-037, R-K4-072) | Tradability; evidence | ICE Brent is neither tradeable on Topstep nor in GLBX.MDP3. K4-030 finds that CME WTI "still dominate[s] price discovery" when the two are cointegrated, which argues against a Brent lead. |
| X-12 K4-rblead-01 | CL traded on RB's microstructure lead (K4-020 P-K4-020-a, P-K4-020-d) | D9.3/D9.4; rule 4; rule 1 | The excitation is measured at one-second resolution (P-K4-020-c). A rule at that scale is high-rate and needs limit fills. The paper runs no predictability test, so no minute-scale horizon or threshold can be traced. It enters K4-ml-01 as a feature only (rb_ret30). |
| X-13 K4-ngwx-01 | NG traded on weather-forecast model updates (K4-038 P-K4-038-b) | Rule 1; rule 3 | The logged link is seasonal cointegration with daily price fluctuation. Model-update times and an obtainable record of historical forecast vintages are [unverified]. The reader's dedicated weather-model-update search did not complete (log section 1, row +). |
| X-14 K4-ngfri-01 | NG continuation after the holiday-week Friday storage releases, to which "the market responds 74% weaker" (K4-029 P-K4-029-a) | Rule 1; flat by F; frequency | The source uses daily regressions only, and whether the missing response is recovered later is [unverified]. Recovery on the next trading day would need a weekend hold. There are a few events a year (the 2025 table has two Friday releases, 2025-01-03 and 2025-11-14). |
| X-15 K4-anticip-01 | Trade ahead of local price trends identified in the CL order book (K4-044 P-K4-044-a) | Data; rule 1 | It needs account-level and order-book data the program does not hold. The trend horizon is [unverified], and the source reports attrition ("difficulty maintaining the anticipatory strategies"). |
| X-16 K4-optmom-01 | CL intraday returns predicted from option-implied higher moments (K4-048) | Rule 1; data | Blocked at title only; nothing retrieved. CL options data is not in the plan. |
| X-17 K4-chpmi-01 | CL traded on the Chinese PMI release, "The effect on the crude oil market is also strong with a coefficient of 0.11" (K3-007 P-K3-007-h [K4]) | Rule 3; rule 1 | It is a surprise response against a consensus that is proprietary. With a price proxy, nothing is left to trade: the K3 log reports the impact "appears to be permanent" (first-run passage, not re-checked). The pre-announcement CARs are "available upon request" (P-K3-007-g, [K3] only). |
| X-18 K4-tam-01 | CL, RB or HO around the London Trading-at-Marker minute (K4-047 P-K4-047-a) | Rule 1; D6 | Documentation only: "No source tests whether they carry a price effect" (log). A clock-drift member is D.1 family A, which D6 does not port. The minute is used only in K4-ml-01's window placement. |
| X-19 K4-abnret-01 | Oil momentum after an intraday-detected abnormal daily return, same day and next morning (K5-028 P-K5-028-a, P-K5-028-e, P-K5-028-f [K4]) | Rule 1 (parameters) | The trigger's threshold construction and oil's timing parameters are not in the [K4] passages; only gold's timing is logged (P-K5-028-d [K5]). The data are MetaQuotes broker prices with no named instrument. There are no costs (P-K5-028-c). The same-day continuation is family C (**covered by CP1**), and the next-day follow-through is family H (**covered by CP3**). |

---

## 3. Beyond budget (lead decides)

None. The log supports 6 new members inside the budget of 11. These candidates were considered and
not written (none is a budget overflow):
- **RB and HO versions of K4-apipre-01, K4-eiafade-01 and K4-eiamom-01.**
  - What the log supports: the WPSR moves RB and HO (K4-002), and Topstep lists RB for the crude
    release (F6).
  - What it lacks: each tradeable mechanism (API under-absorption, post-release overreaction, USO
    half-hour momentum) is documented on crude only (K4-009, K4-022, K4-021). Extending them is an
    inference the evidence does not test.
  - Cost: +1 trial per exposure per member, up to 6 (section 7, item 7).
- **A through-release variant of K4-apipre-01.** It would exit at T_W + 10 instead of T_W - 1, on
    the "predict inventory surprises" half of P-K4-009-a. Not written: the release response is
    contemporaneous, and the D9.4 caution applies to any fill near the release. It would be 1 more
    trial.
- **A percent-of-open breakout on CL**, K4-013 / D.1 B4's own formulation ("a predetermined price
    threshold a percentage above/below the opening price", D.1 row B4). Not written: the threshold
    value is in no verified passage (the D.1 row is truncated, and the first reader's K4-013
    passages were never re-verified). The family is covered by CP2.
- **An index-roll member**, which has insufficient evidence (X-08).

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Alquist, Ellwanger, Jin (2020), JFM (registry K4-008, not read) | WPSR-identified oil shock (K4) -> equities, Treasuries, FX (K1, K2, K3) | oil inventory news as an instrument for cross-asset responses |
| Alturki, Kurov (2022), K4-009, stock-market leg | CL (K4) and the stock market (K1) | the inefficiency spans CL and stocks; the CL-only part is K4-apipre-01 |
| Quantpedia, "Crude Oil Predicts Equity Returns" (R-K4-004) | crude (K4) -> equity index (K1) | crude as an equity timing signal |
| Basistha, Kurov, Wolfe (2024), J. Commodity Markets | oil (K4), equities (K1), monetary policy (K2) | time-varying causal links |
| JFM 2023 (fut.22410), "Trading around the clock ..." | WTI (K4) and G7 equity indices (K1) | session-specific volatility spillover |
| Rosa (2013), K4-025, the dollar channel; plus X-06's surprise measure | FOMC surprise from fed funds futures (rates) and USD (K3) -> CL, HO, NG (K4) | the energy response to FOMC runs through the dollar; the surprise is a rates instrument |
| J. Banking & Finance (2014), airline stocks | crude returns (K4) -> airline equities (non-CME) | crude returns driving stock trading intensity |
| JFM (2010), corn and crude volatility spillover | CL (K4) and ZC (K6) | ethanol-era volatility spillover |
| J. Agricultural Economics (2025, agr.70089) | WTI (K4) and grains (K6) | volatility spillover |
| Chiang, Hughen, "Do Oil Futures Prices Predict Stock Returns?" | CL (K4) -> equities (K1) | oil futures as an equity predictor |
| Quantpedia, "Financialization of crude oil market" | VIX and S&P 500 (K1) and CL (K4) | financial variables explain crude variance |
| Quantocracy / Milton FMR, "Pairs Trading ... CAD - Crude Oil" | 6C (K3) and CL (K4) | CAD-crude pairs |
| arXiv 1209.0900, biofuels-fuels-food | RB, CL (K4) and ZC, ZW, ZS (K6) | wavelet co-movement, ethanol link |
| Kurov, Stan (2018), K3-035 [K4] | monetary-policy uncertainty (a rates-derived measure) conditioning crude's macro response (K4) | the conditioning variable comes from rates; a CL-only use has no base member (section 5) |

The first 13 rows are the reader's own flags (log section 4). Rows 6 and 14 add this catalog's
routing of X-06 and K3-035.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K4.md section 3, every `[K4]`-tagged
passage elsewhere, and the status lines for K4's other registry ids.

| Item | Disposition |
|---|---|
| K4-001 Prokopczuk, Wese Simen, Wichmann | Used: K4-ngpre-01 (P-a to g; the post-2011 null P-e is stated as the prior); K4-ml-01 ngs_phase window (P-c) |
| K4-002 Halova Wolfe, Kurov, Kucher | Used: K4-ngrev-01 (event window P-b; response sign P-d); K4-apipre-01 (window convention P-b); K4-ml-01 wpsr_move and ngs_phase (P-b, P-e). The surprise-signed trade is excluded, X-02 |
| K4-003 Bessembinder et al. (USO rolls) | Excluded as a member, X-08 (resiliency P-b, roll cost P-c, TAS P-d). Used in K4-ml-01 gsci_roll (P-c, P-d) and the ML window placement (the settlement window) |
| K4-004 Linn, Zhu | Used for timing only: K4-ml-01's h (P-a). No directional claim, and the open and close effects are from the pit era: insufficient evidence for a member |
| K4-005 Gay, Simkins, Turac | Excluded, X-01 (proprietary analyst data) |
| K4-006 Ederington, Lin, Linn, Yang | Used: K4-ngrev-01 (the week-to-week reversal, P-a). The disagreement-conditioned part is excluded, X-03 |
| K4-007 Miao, Yang (2026) | Insufficient evidence for a member: EIA releases move returns and liquidity with no directional or predictive claim (P-a). It supports the release-time design of the event members |
| K4-009 Alturki, Kurov | Used: K4-apipre-01 (P-a); K4-ml-01 api_move. The stock-market leg is routed to K8 |
| K4-010 Basistha, Kurov | Excluded, X-06 (surprise from rates; K8) and X-07 (scheduled-meeting null, P-c) |
| K4-012 Gu, Kurov | Excluded, X-01 (proprietary predictor). Its reported Sharpe 1.26 is [unverified] per the log |
| K4-013 Holmberg, Lönnbark, Lundström (see D.1 B4) | **Covered by CP2** (family B, ORB on crude). The percent-of-open variant is not written (section 3) |
| K4-014 Ewald et al. (Brent clock seasonality) | Not used: D.1 family A, which D6 does not port. The clock times are not in the passages (abstract only), and the instrument is ICE Brent. Insufficient evidence for a K4 member |
| K4-017 / K4-018 / K4-045 (EIA and API schedule documentation) | Used for timing in every event member (C9) and in K4-ml-01 wpsr_phase, ngs_phase and api_move |
| K4-020 Jang, Lee, Lee (Hawkes, RB and CL) | Excluded as a member, X-12. Used in K4-ml-01 rb_ret30 (P-a, P-d) |
| K4-021 Wen, Indriawan, Lien, Xu | Used: K4-eiamom-01 (P-a to e); K4-ml-01 wpsr_move and the h choice |
| K4-022 Rousse, Sévi | Used: K4-eiafade-01 (P-a, c, d); K4-apipre-01's pre-release window (P-b, P-e); K4-ml-01 wpsr_phase and wpsr_move. The surprise-conditioned pre-release drift needs an ex-ante predictor; the obtainable one is K4-apipre-01's |
| K4-023 Ye, Karali (poster) | Used: K4-apipre-01 (API time and response, P-a, P-b); K4-eiafade-01 (frequency of large responses, P-c; window, P-b); K4-ml-01 api_move and wpsr_move. The API release itself cannot be traded (after F) |
| K4-024 Bjursell, Wang, Zheng (VPIN) | Insufficient evidence for a member: a volatility and toxicity state with no directional claim (P-a). D6 does not port family D gates. B4 in the ML member carries volatility state |
| K4-025 Rosa (FRBNY SR 598) | Excluded, X-06 (surprise from rates, dollar channel; K8) and X-07 (reversal on a handful of LSAP events). Routed to K8 |
| K4-026 Miao, Ramchander, Wang, Yang | Supporting evidence for K4-apipre-01 (day -1 anticipation, P-c). Not intraday-feasible as tested (daily settlement returns). The surprise-signed version is excluded, X-02 |
| K4-027 Pirrong (TAS) | Excluded, X-09 (no public TAS concentration data). Its settlement-window flow enters X-08's reasoning |
| K4-028 Chiou-Wei, Linn, Zhu | Not intraday-feasible as tested (daily). Used as negative evidence against a multi-day NG post-release drift (P-b), in X-02 |
| K4-029 Gu, Kurov, Stan (Friday releases) | Excluded, X-14 |
| K4-030 Liu, Schultz, Swieringa | Excluded as a signal source, X-11. It is evidence against a Brent lead |
| K4-031 Fernandez-Perez, Garel, Indriawan | Not a mechanism: an input evaluation. Used in X-01 to rule out crowd forecasts as a consensus substitute |
| K4-032 Armstrong, Cardella, Sabah | Excluded, X-05 |
| K4-033 Chang, Daouk, Wang | Excluded, X-04. Its 15-minute post-release window (P-a) informs K4-eiafade-01's measurement window and K4-ml-01 wpsr_move |
| K4-034 Dubois, Maréchal | Excluded as a member, X-08 (null after SE adjustment, P-a). Used in K4-ml-01 gsci_roll (roll days, P-b). [K5] and [K6] passages belong to those writers |
| K4-035 Mou (Goldman roll front-running) | Not intraday-feasible: multi-day calendar spreads (P-b). X-08. [K5] and [K6] passages belong to those writers |
| K4-036 Stoll, Whaley | Excluded as a member, X-08. Used in K4-ml-01 gsci_roll (crude roll impact, P-c). [K6] passages belong to K6 |
| K4-037 Wen, Gong, Ma, Xu | **Covered by CP1** (first half-hour, mostly overnight, predicts the last half-hour, P-a). Counter-evidence for K4-eiamom-01 (P-b) |
| K4-038 Song, López de Prado, Simon, Wu | Excluded, X-13 (weather). The TWAP first-second clock (P-a) is seconds-scale and not tradeable under D9 |
| K4-040 Chan, Gray | Insufficient evidence: a null for scheduled macro releases on energy jumps (P-a). Used in X-07 |
| K4-041 Chatrath, Miao, Ramchander | Insufficient evidence: mostly a null for crude's macro-news response (P-a, abstract via OpenAlex). No member |
| K4-042 Baviera, Santagostino Baldi | Excluded, X-10 |
| K4-043 Fett, McPhail (CFTC stop orders) | Background for CP2 (family B): CL has the highest stop-order share (P-b). Descriptive, no member. The [K2] passage belongs to K2 |
| K4-044 Fishe, Haynes, Onur | Excluded, X-15 |
| K4-046 CME OpenMarkets, API and EIA | Supporting (untested practitioner claim) for K4-apipre-01 and api_move (P-a). P-b's 0.6-0.8 correlation is unsourced and unused |
| K4-047 CME TAM FAQ | Excluded as a member, X-18. Used only for K4-ml-01's window placement (P-a) |
| K4-048 Wong (blocked) | Excluded, X-16 |
| K4-049 Ewald, Zhang (blocked) | Insufficient evidence: title only (forward-premium dynamics); nothing retrieved |
| K4-050 Fetna (blocked) | Insufficient evidence: title only. It is relevant as a prior for CP2 if ever retrieved |
| K4-008 | Routed to K8 (the reader's flag; not read) |
| K4-011, K4-015, K4-016 (tagged K4 and K6), K4-019, K4-039 | Rejected in the log (R-K4-019, R-K4-037, R-K4-038, R-K4-039, R-K4-040). Not used. K4-016 (pre-holiday effect, multi-day ETF hold) has no [K6] passage |
| K3-007 [K4] Baum, Kurov, Wolfe (Chinese macro), P-K3-007-h | Excluded, X-17 |
| K3-035 [K4] Kurov, Stan (policy uncertainty), P-K3-035-a | Insufficient evidence as a K4 member: a conditioning variable for macro-release responses, and K4 has no macro-release member (K4-040 and K4-041 are nulls). The uncertainty measure is unspecified and rates-derived, so it is routed to K8 |
| K3-040 [K4] Kosowski et al., "Overnight-Intraday Reversal Everywhere" | Insufficient evidence: title only, content [unverified]. Note that CP1's (a) form bets the opposite way, overnight continuation |
| K5-028 [K4] Caporale, Plastun, P-K5-028-a, b, c, e, f | Excluded as a threshold member, X-19. Its mechanisms are **covered by CP1** (same-day continuation) and **CP3** (next-day follow-through) |
| K5-029 [K4] Borgards, Czudaj, Hoang, P-K5-029-a, b, c, d | Used: K4-ovr-01 (CL, HO, NG); K4-ml-01 ret60_pct |
| `[K4]` search in K2, K6, K7 logs and the K3 and K5 partial logs | No further `[K4]`-tagged passage. The K2 log's mentions are K4-008 and K4-015/016 pointers; K5's R-K5-010 and R-K5-042 are K4-region rejections by K5, not passed items |
| R-K4-001 to R-K4-075 | Rejected at pre-filter or on reading. Not used. R-K4-061 is cited only for C10's guard |

**Correlated members, flagged for the lead's Tier-A accounting (not a duplication).** K4-eiafade-01
and K4-ovr-01's 10:00 decision on WPSR Wednesdays both fade the release move. They use different
windows, thresholds and holds, so they are separate hypotheses. K4-ngpre-01 and K4-ngrev-01 both
hold NG across the storage release: one always short, the other signed by last week's response.

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all four admitted) |
|---|---|---|---|
| K4-cp1-01 | crude, gas, RBOB, ULSD | 1 | 4 |
| K4-cp2-01 | crude, gas, RBOB, ULSD | 1 | 4 |
| K4-cp3-01 | crude, gas, RBOB, ULSD | 1 | 4 |
| K4-ngpre-01 | gas | 1 | 1 |
| K4-ngrev-01 | EXCLUDED by the lead (review R-06) | - | 0 |
| K4-apipre-01 | crude | 1 | 1 |
| K4-eiafade-01 | crude | 1 | 1 |
| K4-eiamom-01 | crude | 1 | 1 |
| K4-ovr-01 | crude, ULSD, gas | 1 | 3 |
| ~~K4-ml-01~~ [excluded, U6] | crude (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **21** = 12 port + 8 new + 1 ML. In general 3E + 5a_C + 3a_G + a_H. Without RBOB and ULSD: 14. Crude only: 8 |

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **MCL's unresolved * restriction.**
   - Every crude member carries the MCL flag (D9.8), because D2 may pick MCL for crude.
   - If the user cannot clear it before E.1, D2 must choose between CL and QM.
   - K4-ml-01 has no fallback exposure.
2. **CP2's buffer and the ML features are in the vehicle's ticks.**
   - QM's tick (0.025) is 2.5 times CL's and MCL's (0.01). QG's (0.005) is 5 times NG's and MNG's
     (0.001).
   - So CP2's trades on one underlying depend on which contract D2 picks, while every new member is
     tick-free (C8).
   - The text is copied unchanged from D6. The lead decides whether the port's "4 ticks of P" means
     the vehicle's tick (the literal reading, used here) or the full-size contract's tick for every
     contract of an exposure.
3. **CP1 enters at the FOMC statement minute on energy.**
   - With C = 13:30 the entry fill is the 13:00 open, which on scheduled FOMC days is the statement
     minute.
   - This is copied verbatim and allowed at 1 lot-equivalent. The lead decides whether energy ports
     skip FOMC days, which would be a D6 change.
4. **Event-member frequency (C11).**
   - Five of the six new members trade weekly or less: K4-ngpre-01, K4-ngrev-01, K4-apipre-01 and
     K4-eiamom-01 on about 18-21% of dates, and K4-eiafade-01 on about 5%.
   - By arithmetic they need about 5 x eps_X (weekly) and about 20 x eps_X (K4-eiafade-01) per event
     to reach eps_X a day. They are likely "null at eps" or "inconclusive by design" (D4).
   - They cost 5 trials. The lead decides whether they stay at one trial each.
5. **Cost sample for gas.** D8's five dates are all Wednesdays, so NG's Thursday release minute is
   never sampled (C12). The lead decides whether to add a Thursday to the gas vehicles' mbp-1 sample
   (a small spend, quoted in E.1), or to accept a possibly understated release-window cost for
   K4-ngpre-01 and K4-ngrev-01.
6. **K4-ngpre-01's binding evidence is its own authors' null after 2011** (P-K4-001-e). It is
   written because it is the log's only fully specified, full-text, energy-specific intraday rule
   with a stated window. The lead may cut it (1 trial).
7. **RB and HO extensions.** Extending K4-apipre-01, K4-eiafade-01 and K4-eiamom-01 to RB and HO
   is not written: the evidence is for crude only. Adding them would cost up to 6 trials (section 3).
8. **Index roll (X-08).** If the lead wants a K4 roll member once E.2 fixes the roll convention, it
   needs three things first: the S&P GSCI per-commodity contract schedule logged, a verified
   intraday source, and a check that the roll blackout leaves the 5th-9th trade dates in play.
9. **Unfinished research seed.** The reader could not run the weather-model-update search for
   natural gas (search tools exhausted). No gas weather member exists (X-13).
10. **E.2 checks named in this catalog:**
    - (a) EC-WPSR and EC-NGS tables from the yearly Wayback captures (C9), cross-checked against
      actual publication, with the drop rules of C9.
    - (b) EC-NYSE early closes (K4-eiamom-01).
    - (c) Standard-week Mondays against the federal holiday list (EC-API).
    - (d) Tick-size history 2019-2026 (C7).
    - (e) NYMEX dynamic circuit breakers against Topstep's 2% price-lock rule (C13).
    - (f) Member-level coverage for the off-day-session windows: 07:15-08:00 (K4-ml-01), 07:30
      (K4-apipre-01), Tuesday 15:24-15:39 (K4-apipre-01's signal) and 14:30-14:59 (K4-eiamom-01).
    - (g) The C10 guard against the April 2020 bars.
    - (h) MCL's and MNG's short histories and the full-size price-path declaration (C8; D2 and D4).
    - (i) How TopstepX counts QM and QG against the lot limit (C6).
    - (j) RB history for K4-ml-01 if RBOB is not admitted.
11. **Registry hygiene** (already noted by the reader): the author fields for K4-042 ("Lipton?";
    correct: Baviera and Santagostino Baldi) and K4-044 (correct: Fishe, Haynes and Onur) are wrong.
    K4-039 was claimed before it was rejected.

---

# Cluster K5

# Stage E.0 hypothesis catalog, cluster K5 (metals: GC, MGC, SI, SIL, HG, MHG, PL)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K5-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U2: platinum (PL) is OUT, as a traded exposure and as a signal leg (Topstep's 50K volatility cap for PL is 0 and PL has no micro). Every statement below that makes platinum a traded exposure is struck through with a [U2] note; descriptive platinum facts (auction clock times, fees, Topstep's quoted text, question texts) are kept for the record and bind nothing. U9 (review R-28): K5-preauc-01's trial count is 2, as the 01:47 ruling set it.
> **K5 after the decisions: 7 active members, 16 confirmation trials** (4 new + 3 core ports; 9 port + 7 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K5-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:23 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** No price, bar, tick or order-book data for any K5 product
existed on this machine while it was written, and none was opened. The only product-specific numbers
used are:
- contract specifications and public ADV (reports/stage_e0_liquidity.json; design D1 table);
- Topstep's published fees, hours, release table and risk-adjustment rules
  (reports/stage_e0_topstep_facts.md F3, F4, F6, F12);
- calendar metadata: LBMA auction clock times, UK bank-holiday dates, FOMC, BLS and Fed G.17 release
  dates and clock times.

Calendar metadata carries no prices. No price level, range, trend or volatility of any product is used or
assumed below. **No K5 rule reads an LBMA auction result, a CME settlement price, or any released
macro value.** The calendars supply dates and clock times only.

**Inputs read in full:**
- reports/stage_e0_research_K5.md (supersedes the sonnet partial log, which was not used).
- Every `[K5]`-tagged passage elsewhere: K3-007 (P-K3-007-h, reports/stage_e0_research_K3.md); K4-034
  and K4-035 (index-roll passages, reports/stage_e0_research_K4.md, lines 505-536); K4-036's line saying
  it has no metals. The registry also tags K3-040 (title only) and K4-039 (rejected as R-K4-040) with K5.
- reports/stage_e0_source_registry.jsonl (K5 lines and every non-K5 line tagged K5).
- docs/STAGE_E_DESIGN.md: D1-D15, including the 21:12 and 21:52 amendments and D9 points 5a, 8, 11, 12, 13.
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md (F3 fees, F4 hours, F6 news, F7 prohibited, F12 risk adjustments,
  CPI window, holidays).
- reports/stage_e0_liquidity.json (K5 rows).
- reports/stage_d1f_confirmation_list.md 2.1 A3 (Family H mechanics).
- strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py (the CP2 hold count).
- reports/stage_d1b_family_f_declaration.md F3.3 (CP1's origin).
- reports/stage_e0_STATE.md, for the lead's rulings of 21:12 and 21:52.
- reports/stage_e0_catalog_K4.md and reports/stage_e0_catalog_K2.md, for format only. No mechanism was
  taken from them. K5-029 is a K5-claimed panel source that K4 also used for its own products; where this
  catalog makes the same judgment K4 made about that source, the entry says so.

**Official pages fetched in this task** (curl, 2026-09-24 01:28-01:33 PDT). They were fetched only to
confirm auction and release times and calendar availability; no mechanism research was done. Saved under
the scratchpad `fetch/` directory with a `k5_` prefix.
- https://www.ice.com/iba/lbma-gold-silver-price (HTTP 200): "The auctions are run at 10:30 and 15:00
  London time for gold, 12:00 London time for silver, and 09:45 and 14:00 London time for platinum and
  palladium."
- http://web.archive.org/web/20190718185125id_/https://www.theice.com/iba/lbma-gold-silver-price (HTTP 200):
  "The auctions are run at 10:30am and 3:00pm London time for gold and at 12:00pm London time for
  silver." So the gold and silver times are the same in July 2019 and now.
- http://web.archive.org/web/20210414221544id_/https://www.lbma.org.uk/prices-and-data/lbma-platinum-and-palladium-price
  (HTTP 200): "The LBMA Platinum and Palladium Price is administered independently by the London Metal
  Exchange (LME)." The captured text gives no auction times. Platinum's 09:45 and 14:00 are verified only
  on the current pages (K5 log 3.0 and the IBA page above). E.2 confirms 2019-2026 (section 7, item 9).
- https://www.gov.uk/bank-holidays.json (HTTP 200): 83 England-and-Wales dates, 2019-01-01 to 2028-12-26.
- https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (HTTP 200): meetings 2021-2026.
  Scheduled two-day meetings, eight a year; 2025 also lists "August 22 (notation vote)".
- https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm and ...2020.htm (HTTP 200); the
  2021-2024 historical URLs returned 404, but the calendar page above covers those years.
- https://www.federalreserve.gov/newsevents/pressreleases/monetary20190731a.htm and
  .../monetary20250507a.htm (HTTP 200): both read "For release at 2:00 p.m. EDT".
- https://www.bls.gov/schedule/news_release/cpi.htm (HTTP 403 "Access Denied"). The Wayback captures
  http://web.archive.org/web/20190820223142id_/https://www.bls.gov/schedule/news_release/cpi.htm and
  http://web.archive.org/web/20190613093518id_/https://www.bls.gov/schedule/news_release/empsit.htm
  (HTTP 200) list every CPI and Employment Situation release with "Release Time ... 08:30 AM".
- https://www.federalreserve.gov/releases/g17/default.htm (HTTP 200): "The monthly releases are issued
  at 9:15 a.m." and "Historical release dates are also available."
- https://www.census.gov/manufacturing/m3/adv/index.html (HTTP 404). The durable-goods schedule is not
  confirmed (section 7, item 2).

---

## 0. Header

| Item | Value |
|---|---|
| Products | GC, MGC, SI, SIL, HG, MHG (COMEX); ~~PL (NYMEX)~~ [OUT, U2] |
| Exposures | gold {GC, MGC}; silver {SI, SIL}; copper {HG, MHG}; ~~platinum {PL}~~ [OUT, U2] (partition section 1) |
| D1 | **D1 applied: all four K5 exposures IN; platinum flagged (may be suspended).** [U2, 2026-09-24: platinum OUT by the user's decision; three K5 exposures are traded.] Admissible vehicles, 2026 Jan-Aug ADV (design D1 table): gold MGC 429,702 and GC 212,764; silver SIL 134,882 and SI 83,587; copper HG 77,679 and MHG 21,803; platinum PL 22,360 |
| Members | **8 = 4 new + 3 core ports + 1 ML member.** [E.1: 7 = 4 new + 3 core ports; K5-ml-01 excluded, U6.] Budget 15, so 7 slots are unused (section 3) |
| Trials in N (confirmation) | ~~**22 if D2 admits all four exposures:** 12 port + 9 new + 1 ML.~~ [E.1. U9 (review R-28): after the 01:47 ruling put K5-preauc-01 at 2 trials the figure was 21 = 12 port + 8 new + 1 ML. After U2 and U6: **16 if D2 admits gold, silver and copper: 9 port + 7 new**; in general 4E + 3a_G + a_S, where E counts admitted exposures among gold, silver and copper. The E.0 formula follows.] In general 4E + 3a_G + a_S + a_P + 1, where E is the number of admitted exposures and a_G, a_S, a_P are 1 when gold, silver or platinum is admitted (the ML member assumes gold, section 7 item 7). Each exposure of K5-preauc-01 also needs its member-level coverage check (C14) |
| ML grid | ~~48 configurations, counted only in the K5 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Starred products | **MGC and SIL** (Topstep F1). The star's referent is Topstep's "Risk Adjustments: High Risk/High Volatility" article (D9.8, F12.1), encoded as D9.11 and D9.12. **MGC:** volatility cap 30 contracts on the 50K account, so the 1-lot cap of 10 binds first; at most 3 contracts in an opening fill inside the CPI window. **SIL:** volatility cap 2 contracts, which binds, since D2's 1-lot cap would allow 5; the same CPI-window cap of 3; counts 0.2 lot. MHG is unstarred but the same article names it: cap 2 contracts, CPI-window cap 3 |
| Suspension risk (D9.11) | "Silver (SI) = 0; ... Copper (HG) = 0; ... Platinum (PL) = 0" at Topstep's discretion in extreme volatility (F12.1). D2 prefers SIL and MHG whenever they are candidates. **Platinum has no micro and may be suspended in volatile periods**; every platinum trial carries that flag |
| CPI window (D9.12) | No opening fill on GC, SI, HG or PL in [CPI - 5 min, CPI + 5 min] = [07:25, 07:35] CT (CPI 08:30 ET, C9). Such an entry is skipped for the day, not deferred. On MGC, SIL and MHG an opening fill in the window is at most 3 contracts. Only K5-cp2-01 on copper can open inside the window (C11) |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. Every entry is written for every exposure its evidence names, each traded only if D2 admits the exposure |

### Common conventions (apply to every entry unless it says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event
  (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values can be used
  from then on. US Eastern times convert to CT by subtracting one hour, since both zones change clocks on
  the same dates. London times convert by C10.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open, the engine convention
  that D6 and D15.3 use. "Market intent on the bar at X" fills at the open of the bar at X + 1 min.
- **C3 Trade date and hours.**
  - Trade date d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md).
  - Metals Globex hours: "CME Globex Open: Sunday 5:00 p.m. - Friday 4:00 p.m. CT with a daily
    maintenance period from 4:00 p.m. - 5:00 p.m. CT" (K5 log 3.0, CME weekly metals options fact card).
    E.2 confirms the futures hours; the futures pages did not show them in the captures read.
  - So the first bar of trade date d is the 17:00 CT bar of d-1 (Sunday for a Monday). A London-morning
    auction on calendar date d (03:45-07:00 CT) falls in trade date d.
- **C4 Exclusions for the four new members.** The ports follow D6 as written. A new member does not trade
  on:
  - roll-blackout dates (`screen_candidate` with `roll_blackout`, the program convention);
  - dates the D10 metals calendar marks as early close or early halt (Family H's "Days with
    early_halt_ct set: no trade");
  - dates on which a bar the rule reads, or its entry-intent bar, is missing, or on which the signal bars
    of one computation carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced flatten
  at F is the backstop.
- **C5 Flat time.** F = 15:08 CT for every K5 product (D9.1; D6 rows: gold O 07:20, C 12:30; silver O
  07:20, C 12:25; copper O 07:10, C 12:00; platinum O 07:20, C 12:05). No new member's last fill is later
  than 13:19 CT.
  - The log verifies C for gold and copper against CME's settlement periods: GC "13:29:00 to 13:30:00 ET"
    (12:29-12:30 CT) and HG "12:59:00 to 13:00:00 ET" (11:59-12:00 CT) (K5 log 3.0).
  - Silver's 12:25 and platinum's 12:05 are not verified in E.0. D6 says E.2 confirms them.
- **C6 Size.** q_c of the exposure's D2 vehicle, never above 1 lot-equivalent (D2, D9.5) and within the
  50K volatility caps (D9.11). No member sizes by signal.

  | Contract | Lot-equivalent (D9.6) | D2 cap (1 lot) | D9.11 cap, 50K | Largest q_c |
  |---|---|---|---|---|
  | GC | 1 | 1 | 3 | 1 |
  | MGC* | 0.1 | 10 | 30 | 10 |
  | SI | 1 | 1 | 0 at Topstep's discretion | 1 (may be suspended) |
  | SIL* | 0.2 | 5 | 2 | **2** |
  | HG | 1 | 1 | 0 at Topstep's discretion | 1 (may be suspended) |
  | MHG | 0.1 | 10 | 2 | **2** |
  | ~~PL~~ [OUT, U2] | ~~1~~ | ~~1~~ | 0 (Topstep F12.1c) | — |

- **C7 Ticks and fees.** Ticks are from reports/stage_e0_liquidity.json (CME contract specifications,
  fetched 2026-09-23 20:48 PDT). Round turns are Topstep F3.

  | Contract | Tick | Tick value | Topstep round turn | Round turn in ticks |
  |---|---|---|---|---|
  | GC | 0.10 | $10.00 | $4.32 | 0.43 |
  | MGC | 0.10 | $1.00 | $1.92 | 1.92 |
  | SI | 0.005 | $25.00 | $4.32 | 0.17 |
  | SIL | 0.005 | $5.00 | $2.72 | 0.54 |
  | HG | 0.0005 | $12.50 | $4.32 | 0.35 |
  | MHG | 0.0005 | $1.25 | $1.92 | 1.54 |
  | PL | 0.10 | $5.00 | $4.32 | 0.86 |

  - Within each exposure both contracts have the same tick in price units (0.10, 0.005, 0.0005). So CP2's
    buffer, "4 ticks of the exposure's most active contract", and every tick-denominated ML feature mean
    the same price distance whichever vehicle D2 picks.
  - These are 2026 specifications. E.2 confirms each tick was unchanged over 2019-05..2026-06 before any
    bar is read.
- **C8 Price data.** Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is bought
  in E.1, and the confirmation and holdout-2 history of the chosen vehicle in E.2b (D13).
  - **History.** GC, SI, HG and PL exist from 2019-05. MGC was listed 2010-10-04 and SIL in June 2013
    (year inferred, liquidity JSON). MHG was listed 2022-05-02, and its quotes before 2022-04 failed (D13).
    If D2 picks MHG, E.2 may declare HG's bars as the price path for the confirmation window (D2, D4).
  - **Availability.** A bar is available at its close (C1).
  - **Tick-free rules.** The new members' signals are signs (K5-pmfix-01, K5-fomc-01), percent returns
    (K5-ovr-01) or nothing (K5-preauc-01). They give the same decision on either contract of an exposure.
  - mbp-1 enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C9 Event calendars.** All are external and free. Each supplies dates and scheduled clock times only.
  - **EC-LBMA, LBMA auction start times (London).** Gold 10:30 (AM) and 15:00 (PM); silver 12:00; platinum
    09:45 (AM) and 14:00 (PM).
    - Sources: the IBA page (current and the 2019 capture above) and the LBMA platinum page (K5 log 3.0).
    - The schedule is fixed and known in advance. The results "do not have set publication times" (LBMA
      page, K5 log 3.0), so no rule times itself on a result, and no rule reads one.
    - A scheduled auction day is a weekday that is not an England-and-Wales bank holiday in EC-UKBH.
    - A member trades every scheduled auction day as scheduled. No day is dropped after the fact, for
      example because an auction started late; that would be look-ahead.
    - E.2 confirms the platinum times for 2019-2021 (LME era) and checks for any UK half-day or special
      schedule announced in advance (IBA and LME notices). A day announced in advance as having no auction
      is not a scheduled auction day.
  - **EC-UKBH, UK bank holidays.** https://www.gov.uk/bank-holidays.json, England and Wales, 2019-01-01 to
    2028-12-26. The file lists dates years ahead, which shows they are published in advance.
  - **EC-FOMC, scheduled FOMC statement days.**
    - Sources: federalreserve.gov FOMC calendars (2021-2026 on the calendar page; 2019 and 2020 on the
      historical pages). The statement release time is read from each statement page ("For release at 2:00
      p.m. EDT", verified for 2019-07-31 and 2025-05-07). 14:00 ET = 13:00 CT.
    - Included: the second day of each scheduled meeting, when that page shows a 14:00 ET release.
    - Excluded: unscheduled meetings and actions, notation votes, and any statement released at another
      time.
    - Known in advance: the calendar is published before the year.
  - **EC-BLS, Employment Situation and CPI.** The BLS release schedules give each release at "08:30 AM" ET
    = 07:30 CT (verified in the 2019 captures above). The live pages refuse curl, so E.2 builds each year
    from Wayback captures dated before the releases.
    - A release whose actual date or time differs from the schedule published before it is handled as K4's
      C9 handles moved releases: the ML feature uses only the schedule known the evening before d.
    - The D8 cost and D9.5a guard use the actual release time, which can only make the harness more
      conservative.
  - **EC-G17, Fed G.17 Industrial Production and Capacity Utilization.** "The monthly releases are issued
    at 9:15 a.m." ET = 08:15 CT; historical release dates are published (page above). Used only for
    copper's D8 cost and D9.5a guard (C11).
  - **EC-CAL.** The D10 metals calendar (trade dates, holidays, early closes and halts), built by E.2 from
    CME schedules.
- **C10 London to Chicago conversion (every date, including the weeks when the US and UK change clocks on
  different dates).**
  - **Rule.** For an auction at London wall-clock time L on calendar date d:
    T_CT(d, L) = the America/Chicago wall-clock time of the instant whose Europe/London wall-clock time is
    L on d, computed with the IANA time-zone database (Python `zoneinfo`: build
    `datetime(d, L, tzinfo=ZoneInfo("Europe/London"))`, then `.astimezone(ZoneInfo("America/Chicago"))`).
  - **Equivalent statement.** London minus Chicago is 6 hours, except 5 hours from the US spring change
    (second Sunday of March) to the UK spring change (last Sunday of March), and from the UK autumn change
    (last Sunday of October) to the US autumn change (first Sunday of November).
  - **Weekday ranges with the 5-hour offset** (computed with `zoneinfo`; calendar arithmetic only):

    | Year | Spring (weekdays) | Autumn (weekdays) |
    |---|---|---|
    | 2019 | 2019-03-11..03-29 (15) | 2019-10-28..11-01 (5) |
    | 2020 | 2020-03-09..03-27 (15) | 2020-10-26..10-30 (5) |
    | 2021 | 2021-03-15..03-26 (10) | 2021-11-01..11-05 (5) |
    | 2022 | 2022-03-14..03-25 (10) | 2022-10-31..11-04 (5) |
    | 2023 | 2023-03-13..03-24 (10) | 2023-10-30..11-03 (5) |
    | 2024 | 2024-03-11..03-29 (15) | 2024-10-28..11-01 (5) |
    | 2025 | 2025-03-10..03-28 (15) | 2025-10-27..10-31 (5) |
    | 2026 | 2026-03-09..03-27 (15) | 2026-10-26..10-30 (5) |

  - **Auction start times in CT:**

    | Auction (London) | CT, normal (6 h) | CT, 5-hour weeks |
    |---|---|---|
    | Platinum AM 09:45 | 03:45 | 04:45 |
    | Gold AM 10:30 | 04:30 | 05:30 |
    | Silver 12:00 | 06:00 | 07:00 |
    | Platinum PM 14:00 | 08:00 | 09:00 |
    | Gold PM 15:00 | 09:00 | 10:00 |

    The log's K5-010 and K5-012 entries give the same conversion. Run 1's "05:00 CT-ish" was corrected
    there.
  - **Worked check.** 10:30 GMT = 04:30 CST (UTC-6); 10:30 BST = 09:30 UTC = 04:30 CDT; on 2025-03-12,
    10:30 GMT = 10:30 UTC = 05:30 CDT.
- **C11 Releases K5 names for D8's event-window cost and D9.5a's fill guard.** D8 reads "Topstep's
  release table, F6.4, plus the releases the product's catalog members name".

  | Release (CT) | Gold | Silver | Copper | Platinum | Basis |
  |---|---|---|---|---|---|
  | Employment Situation 07:30 | yes | yes | yes | no | F6.4 "Unemployment Rate / 7:30 AM" names GC, SI, HG ("**Micro contracts also apply"); P-K5-014-a, P-K5-014-c |
  | CPI 07:30 | yes | yes | yes | yes | D9.12 names GC, SI, HG, PL and the micros; P-K5-015-a ("consumer price index") |
  | FOMC statement 13:00 | yes | yes | yes | yes | F6.4 "FOMC Statement / 1:00 PM / All products"; P-K5-024-a |
  | G.17 industrial production 08:15 | no | no | yes | no | P-K5-014-c: "Copper returns ... are more sensitive to the 9:15 set of announcements which include capacity utilization and industrial production" |
  | The exposure's own LBMA auction starts (C10) | yes | yes | n/a | yes | **D8 cost only, pending the lead** (section 7, item 1) |

  - **Effect on this catalog's rules.** No new-member or ML fill lands in [release, release + 2 min) for any
    row, auction starts included. Every new member and the ML member are timed so.
  - **Ports.** A port fill can land in a guarded minute: CP2 entries around 07:30, 08:15, 09:00 or 10:00 CT,
    and CP2 exits at 13:00-13:01. The harness defers such a fill (D9.5a).
  - **CP2 on copper in the CPI window.** If the vehicle is HG, an opening fill in [07:26, 07:35] on a CPI
    day is skipped for the day (D9.12). A fill deferred by D9.5a to 07:32 would still be inside the window,
    so the skip takes precedence. On MHG (q <= 2 <= 3) the fill is allowed.
  - **Durable goods (08:30 ET)** is also among Elder's largest-impact releases for gold and silver
    (P-K5-014-a). It is not named because its schedule source was not confirmed (Census page 404; section
    7, item 2).
- **C12 Frequency (arithmetic from calendar counts, no price data).**
  - **Research window 2025-04-01..2026-06-19:** 319 weekdays, 12 of them England-and-Wales bank holidays.
    About 305 CME trade dates (K4 catalog C11, same window). About 290-300 dates are both CME trade dates
    and scheduled auction days, before roll-blackout exclusions (E.2 gives the exact count). 20 weekdays
    fall in 5-hour weeks (2025-10-27..31, 2026-03-09..27).
  - **FOMC statement days in the research window, 10:** 2025-05-07, 06-18, 07-30, 09-17, 10-29, 12-10;
    2026-01-28, 03-18, 04-29, 06-17 (fomccalendars.htm).
  - **Confirmation window 2019-05-06..2024-02-29** (the earliest S_X): 1,259 weekdays, 41 England-and-Wales
    bank holidays, 70 weekdays in 5-hour weeks. About 37-38 scheduled statement days (eight a year; E.2
    counts them from EC-FOMC).
  - **Consequence.** A member trading on k of about 305 research dates, with zeros on the rest (D5), needs a
    net P&L per event of about (305 / k) x eps_X to reach eps_X per trade date. That is about 1 x for the
    daily members and about 30 x for K5-fomc-01 (section 7, item 4).
- **C13 Price-limit proximity (D9.7).** Whether COMEX and NYMEX metals carried daily price limits or

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  dynamic circuit breakers over 2019-2026 is not verified in E.0 (outside this task's permitted fetches).
  - E.2 builds the per-product table from CME rules, and decides with the user whether Topstep's "Holding a
    position within 2% of a product's price lock limit" [F2.1] applies to a dynamic band.
  - If it does, it is encoded as D9.7: no entry, and an immediate exit, while the price is within 2% of the
    limit. The catalog assumes no limit either way.
- **C14 Member-level coverage (D9).** Each member's own window must show ohlcv-1m coverage >= 0.95 on the
  research window for its vehicle before it is screened. D1 measured coverage only in 07:20-12:30 CT.
  - Outside that window are K5-preauc-01 (03:15-06:59 CT, by exposure) and the first ML position
    (07:16-07:20).
  - A trial whose window fails is excluded before screening, with the reason logged. Platinum's 03:15-03:44
    window is the likeliest to fail (section 7, item 3).

---

## 1. Members

### K5-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K5. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures** (each a separate trial): gold {GC, MGC}, silver {SI, SIL}, copper {HG, MHG}
  ~~, platinum {PL}~~ [U2: platinum OUT]. Each is traded only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log A10
  and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the trade
    date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the
    signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
    (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
  - **D6 note, verbatim:** "Every port trades q_c of the exposure's D2 vehicle and follows D9 (flat by F,
    trade-through for any limit order, which none of the three uses)." D6's text governs this entry.
  - **K5 log:** K5-028's same-day continuation after an abnormal gold return ("Prices tend to move in the
    direction of abnormal returns till the end of the day when these occur", P-K5-028-a) is the same family
    (intraday continuation). It is recorded as **covered by CP1** for the unconditional form; its threshold
    variant is excluded (X-07). The reader's rejected R-K5-018 (Rosa, generic intraday momentum) is also
    this family.
- **Instantiated** (D6 rows; the first bar of trade date d is the 17:00 CT bar of d-1, C3):

  | Exposure | O / C / F | Signal: open of first bar to close of bar at | Entry intent bar, fill | Exit intent bar, fill | Hold |
  |---|---|---|---|---|---|
  | gold | 07:20 / 12:30 / 15:08 | 07:49 (known 07:50) | 11:59, 12:00 | 12:28, 12:29 | 29 min |
  | silver | 07:20 / 12:25 / 15:08 | 07:49 | 11:54, 11:55 | 12:23, 12:24 | 29 min |
  | copper | 07:10 / 12:00 / 15:08 | 07:39 | 11:29, 11:30 | 11:58, 11:59 | 29 min |
  | ~~platinum~~ [OUT, U2] | ~~07:20 / 12:05 / 15:08~~ | ~~07:49~~ | ~~11:34, 11:35~~ | ~~12:03, 12:04~~ | ~~29 min~~ |

  - **Holding horizon:** 29 minutes on every exposure.
  - **Session window:** the entry-to-exit rows above. Flat at least 2 h 39 min before F (gold's 12:29).
  - The gold exit fill (12:29) is the first minute of GC's settlement period, and copper's (11:59) of HG's
    (C5). This is how the port falls on these products; it is not a design choice.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid; history 2019-05..2026-06
  (MHG from 2022-05, C8). The signal is known at O+30 CT.
- **Order type:** market. **Sizing:** q_c (C6).
- **Parameters:** O+29, C-31 and C-2 as instantiated (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes. Floor:
  at most 20 entries a day, 2-minute minimum and 10-minute mean hold, all ok.
- **Falsification:** the standard condition only (a port; D6 unchanged): UCB95 of the member's mean net
  daily P&L per contract below eps_X at >= 80% achieved null power on the confirmation window counts
  against it.
- **Topstep check:**
  1. Flat by F: last fill 12:29.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills.
  4. Star rules: MGC or SIL if D2 picks them. Size is within D9.11 (C6), and no fill falls in the CPI
     window.
  5. News: <= 1 lot-equivalent, half the 2-lot maximum.
  6. D9.5a guard: no fill in any C11 minute.
  7. CPI window: no opening fill in [07:25, 07:35].
  8. Position and volatility caps: within C6. SI, HG and PL may be suspended at Topstep's discretion.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of each admitted K5 vehicle over the research window 2025-04-01..2026-06-19
  and the confirmation window S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 3 after U2; E.0: at most 4).

### K5-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K5. **Products read:** own vehicle.
- **Exposures:** gold, silver, copper ~~, platinum~~ [U2: platinum OUT], one trial each, each traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py, hold_minutes = 75), as
  fixed in D6 row CP2 with the 21:12 amendment and the 21:52 ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market intent in
    the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes after the fill, or
    the engine's forced flatten at F if earlier."
  - **D6 note, verbatim:** ""4 ticks of P" in CP2 means 4 minimum price increments of the exposure's most
    active contract (D1 table), in price units, fixed whatever vehicle D2 chooses."
  - **K5 log:** no K5 source tests an opening-range breakout on a metals futures contract. K5-008's 60-minute
    Keltner-channel breakout is family G, not this port (X-08).
- **Instantiated:**

  | Exposure | OR bars | Eligible entry bars | Buffer = 4 ticks of the most active contract | Per contract | Earliest / latest entry fill | Latest exit |
  |---|---|---|---|---|---|---|
  | gold | [07:20, 07:35) | opening in [07:35, 12:30) | MGC tick 0.10, so 0.40 | GC $40, MGC $4 | 07:36 / 12:30 | 13:45 |
  | silver | [07:20, 07:35) | [07:35, 12:25) | SIL tick 0.005, so 0.020 | SI $100, SIL $20 | 07:36 / 12:25 | 13:40 |
  | copper | [07:10, 07:25) | [07:25, 12:00) | HG tick 0.0005, so 0.0020 | HG $50, MHG $5 | 07:26 / 12:00 | 13:15 |
  | ~~platinum~~ [OUT, U2] | ~~[07:20, 07:35)~~ | ~~[07:35, 12:05)~~ | ~~PL tick 0.10, so 0.40~~ | ~~PL $20~~ | ~~07:36 / 12:05~~ | ~~13:20~~ |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is <= OR_low -
    buffer sells. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it. The exit intent is emitted on
    the 75th bar after the entry-intent bar and fills at the next open. The engine's flatten at F is the
    backstop and never binds on a full session.
  - **Holding horizon:** 75 minutes.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known at O+15.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks of the most active contract, hold 75 minutes (D6, a literal
  port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: latest exit 13:45.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. Star rules: MGC or SIL per C6.
  5. News: <= 1 lot-equivalent. A position may be open at 07:30, 08:15 (copper) or 13:00 CT releases,
     which F6.3 allows below the full maximum.
  6. D9.5a: entry fills that would land at 07:30-07:31 (Employment Situation or CPI days), 08:15-08:16
     (copper, G.17 days) or at an auction-start minute (if the lead confirms, C11), and exits at
     13:00-13:01 on FOMC days, are deferred by the harness.
  7. CPI window: gold, silver and platinum entries start at 07:36, outside it. **Copper on HG: entries whose
     fill falls in [07:26, 07:35] on CPI days are skipped for the day (C11); on MHG they are allowed.**
  8. Position and volatility caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 3 after U2; E.0: at most 4).

### K5-cp3-01 (core port CP3, prior-close location)
- **Cluster** K5. **Products read:** own vehicle.
- **Exposures:** gold, silver, copper ~~, platinum~~ [U2: platinum OUT], each traded only if D2 admits it. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L over [O,
    C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H. CLV = (C_d -
    L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent on the O bar of day
    d. Exit: first bar at or after C-2 min."
  - **Family H rules carried over** (2.1 A3):
    - A day is complete only if its O bar and C-1 bar exist, it has no early halt, and all its bars in
      [O, C) carry one instrument_id.
    - Instrument guard: d-1's daily bar must carry the instrument_id of day d's O bar.
    - CLV cuts are non-strict.
  - **K5 log:** no K5 source tests a prior-day follow-through on metals. K5-028's next-day effect for gold is
    contrarian, the opposite sign, and "Not rejected" against random (P-K5-028-e, P-K5-028-f), so it is not
    evidence for or against this port (X-07).
- **Instantiated:**

  | Exposure | Daily bar | C_d = close of the bar at | Entry intent bar, fill | Exit intent bar, fill | Hold |
  |---|---|---|---|---|---|
  | gold | [07:20, 12:30) | 12:29 | 07:20, 07:21 | 12:28, 12:29 | 308 min |
  | silver | [07:20, 12:25) | 12:24 | 07:20, 07:21 | 12:23, 12:24 | 303 min |
  | copper | [07:10, 12:00) | 11:59 | 07:10, 07:11 | 11:58, 11:59 | 288 min |
  | ~~platinum~~ [OUT, U2] | ~~[07:20, 12:05)~~ | ~~12:04~~ | ~~07:20, 07:21~~ | ~~12:03, 12:04~~ | ~~283 min~~ |

  CLV is computed with Range[d-1] > 0. CLV >= 0.8 buys; CLV <= 0.2 sells.
  - **Holding horizon:** 283-308 minutes, by exposure (table).
  - **Session window:** from the O + 1 fill to the C - 1 fill. Flat at least 2 h 39 min before F.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar is
  complete at C on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8; lookback 1 (D6, H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 283-308 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 12:29.
  2. Order type: market.
  3. D9.4: ok.
  4. Star rules: C6.
  5. News: holds through the 07:30 releases, the gold PM auction, G.17 (copper) and never FOMC (exits by
     12:29), at <= 1 lot-equivalent.
  6. D9.5a: no fill in a guarded minute.
  7. CPI window: the entry fill at 07:11 or 07:21 is before 07:25.
  8. Caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 3 after U2; E.0: at most 4).

### K5-preauc-01 (short into the LBMA auctions held outside US trading hours)
- **Cluster** K5. **Products read:** the traded exposure's vehicle; EC-LBMA; EC-UKBH; EC-CAL.
- **Traded exposures** (each a separate trial; each only if D2 admits it and its window passes C14):
  - gold {GC, MGC}, into the gold AM auction (10:30 London);
  - silver {SI, SIL}, into the silver auction (12:00 London);
  - platinum {PL}, into the platinum AM auction (09:45 London). [REMOVED by the lead, 01:47 PDT 2026-09-24, answering this writer's question 3: one abstract (Nilsson) supports the member, and platinum carries the coverage and "may be suspended" risks; K5-preauc-01 is kept on gold and silver only, 2 trials.]

  **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed** (K5-002, P-K5-002-a): "We find that there is negative price pressure going into the
    auctions, for all precious metals, outside active US trading hours regardless of Fixing structure. For
    active US trading hours, there is no obvious, observable persistent price pressures." "Regardless of
    Fixing structure" covers both the telephone fix and the electronic auctions of 2014-2015 onward, the
    regime of the program's windows.
  - **Which auctions (reasoning; the passage does not define "active US trading hours").**
    - The three auctions traded here start at 03:45-07:00 CT (C10), before the metals day session opens
      at 07:20 CT (D6). The old COMEX floor opened at 08:20 ET (07:20 CT): "All announcements occur at
      08:30AM (EST), just 10-minutes after the official market open" (P-K5-019-b); "the COMEX opens at
      8:20 a.m. EST" (P-K5-020-a).
    - The gold PM auction (09:00 or 10:00 CT) and the platinum PM auction (08:00 or 09:00 CT) fall inside
      US trading hours. The passage's second sentence says those show no persistent pressure, so they are
      not traded.
  - **Microstructure context (a cost headwind, not evidence for or against the drift).**
    - "quoted spreads are typically at their highest point immediately prior to the start of the fix"
      (K5-012, P-K5-012-f).
    - "we observe a noticeable decline in depth prior to the start of the fix" (P-K5-012-g).
    - The exit is therefore placed one minute before the start (Parameters), and C11 names the auction for
      D8's cost.
  - **What the log does not contradict.** K5-012's post-reform "no significant leakage prior to the start
    of the fix" (P-K5-012-i) concerns informed returns signed by the eventual fix direction. It does not
    address an unsigned downward pressure, so it is not a direct test of this claim. No source in the log
    tests pre-auction pressure after 2015 on its own.
  - **Evidence quality.**
    - Abstract only: SSRN blocked, no mirror (K5 log).
    - A practitioner working paper, never published.
    - The window length, magnitude, costs and data window are [unverified].
    - The lead may cut it (section 7, item 3).
  - **Classification:** new to the program (a London-auction clock effect specific to precious metals). It
    is not a D.1 family A port: its reference clock is the auction, not the product's session. It is
    written as a product-specific test under partition rule 6.
- **Entry rule.**
  - **Days:** each eligible trade date d (C4) on which d is a scheduled auction day (C9 EC-LBMA, EC-UKBH).
  - **Auction time:** T = T_CT(d, L_X) (C10), with L_X = 10:30 (gold), 12:00 (silver) or 09:45
    (platinum). That gives T = 04:30 or 05:30 CT (gold), 06:00 or 07:00 (silver), 03:45 or 04:45
    (platinum).
  - **Order:** SELL q_c. Market intent on the bar at T - 31 min, filling at the open of the bar at
    T - 30 min.
  - **Conditions:** unconditional; there is no signal. If the bar at T - 31 is missing, there is no trade
    that day (no late entry).
- **Exit rule:** market intent on the bar at T - 2 min, filling at the open of the bar at T - 1 min (C4 if
  that bar is missing).
- **Holding horizon:** 29 minutes. **Session window:** [T - 30, T - 1], for example gold 04:00-04:29 CT in
  normal weeks. Flat more than eight hours before F.
- **Data fields read:**
  - The vehicle's ohlcv-1m bar existence and instrument_id at T - 31 and T - 2, and the fills (C8). Paid;
    history 2019-05 on (MHG not involved). Available at each bar's close.
  - EC-LBMA and EC-UKBH (C9). Free, 2019-2026 available, known in advance.
  - EC-CAL (E.2).
  - No auction result is read.
- **Order type:** market. **Sizing:** q_c (C6: SIL at most 2; MGC at most 10; GC, SI, PL 1).
- **Parameters.**
  - **Window of 30 minutes before the auction: a judgment.** It is the pre-fix span of K5-012's event
    window, which the K5 log's product line for K5-012 describes as "a window from 30 minutes before to 60
    minutes after the fix start". That line is the reader's description, not a quoted passage.
    Nilsson's own window is not in the passage.
  - **Exit at T - 1: a judgment.** It is the last full minute before the start. It avoids the start minute,
    where spreads peak (P-K5-012-f), and keeps the member out of any D9.5a window should the lead count
    auction starts as releases (section 7, item 1).
  - **Grid:** none.
- **Expected entries and hold:** 1 per eligible date per exposure: about 290 research and about 1,150
  confirmation dates per exposure before roll-blackout exclusions (C12). Held 29 minutes. Floor ok (1 entry
  a day; 29-minute holds).
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean over traded dates of (open at T - 30 minus open at T - 1), in ticks
    (the gross return of the short), is positive.
  - **Descriptive clock control (not a trial):** the same statistic for the window one hour earlier (open
    at T - 90 minus open at T - 61). It separates an auction effect from a clock-wide overnight drift.
- **Topstep check:**
  1. Flat by F: last fill no later than 06:59 CT.
  2. Order type: market.
  3. D9.4: one trade a day, entered 30 minutes before a scheduled event, not in a gapped market; no stops.
  4. Star rules: SIL at most 2, MGC at most 10 (C6).
  5. News: no C11 release in any window (07:30 is after the latest exit, 06:59). <= 1 lot-equivalent.
  6. D9.5a: no fill in [T, T + 2) or in any C11 minute.
  7. CPI window: all fills before 07:00, outside it.
  8. Caps: C6. **Platinum may be suspended** (D9.11).
  9. Price limit: C13.
  - Also C14: each window lies outside D1's coverage window, and platinum's 03:15-03:44 is the likeliest
    to fail the member-level check.
- **Data needed:** ohlcv-1m of the gold and silver ~~and platinum~~ [U2: platinum OUT] vehicles over 03:00-07:00 CT and the fills'
  buckets, in the research and confirmation windows. D8 needs slippage buckets for 03:00-07:00 CT. External:
  EC-LBMA, EC-UKBH, EC-CAL.
- **Trials in N:** ~~3 (one per exposure)~~ 2 (gold and silver, one each, as the 01:47 ruling set it; text fixed in Stage E.1 under U9, review R-28).

### K5-pmfix-01 (gold PM auction: continuation of the auction's first two minutes)
- **Cluster** K5. **Products read:** the gold vehicle; EC-LBMA; EC-UKBH; EC-CAL.
- **Traded exposure:** gold {GC, MGC}, only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** The seed of the K5 region (partition section 3: "the LBMA gold price auctions ... and their
  effect on COMEX futures (seed: Caminschi and Heaney 2014, JFM)").
  - **For (legacy telephone fixing, GC, 2007-2012, K5-001):**
    - "Trades in the opening minutes of the fixing are significantly predictive of the price direction of
      the fixings, in some cases exceeding 90%" (P-K5-001-a).
    - "trades in GC and GLD following the start of the fixing are found to be predictive of the fixing
      price direction, with higher prediction rates (80-95%) for fixings resulting in larger price
      movements" (P-K5-001-c).
    - An informed advantage of "around 10bps in the four minutes following the start of the fixing, and a
      possible further 4bps in the two minutes before the end" (P-K5-001-c).
    - Trade volume up over 50% and volatility up over 40% after the start (P-K5-001-b).
    - K5-012: in "the former fix period, significant return advantages accrue to informed participants
      ahead of the announcement of the benchmark price ... consistent across all the precious metals"
      (P-K5-012-d).
    - Crain et al. (K5-006), trend-controlled: "the fix change significantly increased volatility of prices
      in silver and gold markets" (P-K5-006-f); "the gold fix change led to an increase in volatility in gold
      futures following the change to the gold fixing process" (P-K5-006-g). So the fix window may remain
      eventful after the reform.
  - **Against (post-reform electronic auction):**
    - K5-012 finds "a reduction in the adjusted returns, volatility, and return predictability of the
      associated futures contract" (P-K5-012-a).
    - "there is no significant leakage prior to the start of the fix and within minutes of the start, most of
      the price discovery process is complete" (P-K5-012-i).
    - "For gold and silver, the fix is almost always complete within ten minutes of the opening submission"
      (P-K5-012-h).
    - The gold post-reform change is "statistically insignificant", attributed to "the small sample of data
      in the post period" (P-K5-012-e).
    - "reforms to the Fix have reduced quoted and effective bid-ask spreads and improved overall market
      depth" (K5-013, P-K5-013-a).
    - Crain et al., raw: "the standard deviations are significantly lower in the post-fix change period"
      (P-K5-006-c).
    - Crain's evidence on both sides is DAILY (P-K5-006-b), so it bears on the fix window only indirectly.
    - Old regime, end of the fixing: "the two minutes leading to the end of the fixing do show statistically
      significant negative returns ... overshoot" (P-K5-001-g), and "no significant returns following the
      end of the fixing" (P-K5-001-c).
  - **What a public trader can use (reasoning).**
    - Caminschi's return advantage belongs to "an informed trader, with directional foresight of the fixing
      price" (P-K5-001-f), which no rule has.
    - What is observable is the price change in the auction's first minutes. The source's predictor is
      trade direction; ohlcv-1m has no trade sign, so the price change is the proxy.
    - The member tests whether the direction of the first two minutes continues over the next ten, that
      is, whether part of the move toward the auction price is still ahead after two minutes.
    - The post-reform evidence leans against it. The member is the direct test of the seed in the
      program's 2019-2026 windows.
  - **Confound, not conditioned on:** in normal weeks T_P = 09:00 CT = 10:00 ET, the release time of several
    US data series that are not in C11. The rule does not condition on them.
  - **Classification:** new to the program.
- **Entry rule.**
  - **Days:** eligible trade dates (C4) that are scheduled gold PM auction days (C9).
  - **Auction time:** T_P = T_CT(d, 15:00) (C10): 09:00 CT, or 10:00 CT in 5-hour weeks.
  - **Signal:** s = close of the bar at T_P + 1 min minus close of the bar at T_P - 1 min, that is, from the
    last pre-auction minute to the end of the auction's second minute. Both bars must exist with one
    instrument_id.
  - **Order:** s > 0 BUY q_c; s < 0 SELL q_c; s = 0 no trade. Market intent on the bar at T_P + 1 (emitted
    at T_P + 2), filling at the open of the bar at T_P + 2.
- **Exit rule:** market intent on the bar at T_P + 11, filling at the open of the bar at T_P + 12.
- **Holding horizon:** 10 minutes. **Session window:** 09:02-09:12 CT, or 10:02-10:12 CT in 5-hour weeks.
  Flat by F.
- **Data fields read:**
  - Gold vehicle ohlcv-1m close and instrument_id at T_P - 1 and T_P + 1 (C8). Paid; available at the
    close of the bar at T_P + 1, which is T_P + 2.
  - EC-LBMA and EC-UKBH (C9). Free, 2019-2026, known in advance.
  - EC-CAL.
  - No auction result is read.
- **Order type:** market. **Sizing:** q_c (GC 1 or MGC at most 10).
- **Parameters.**
  - **Signal span of 2 minutes: a judgment.** It lies inside the source's "4 minutes following the start"
    (P-K5-001-c) and its "opening minutes" (P-K5-001-a). It is also the shortest span that puts the entry
    fill at or after T_P + 2, outside [T_P, T_P + 2) should the auction start count for D9.5a.
  - **Hold of 10 minutes: a judgment.** It is D9.3's minimum mean hold. The exit comes 12 minutes after
    the start, just after the post-reform auction "is almost always complete within ten minutes"
    (P-K5-012-h).
  - **No size threshold: a judgment.** The source's higher prediction rates for larger moves (P-K5-001-c)
    suggest one, but no threshold value is logged, so the split is reported descriptively (Falsification).
  - **Grid:** none.
- **Expected entries and hold:** about 1 per eligible date (about 290 research and 1,150 confirmation dates,
  less s = 0 days). Held 10 minutes. Floor: the 10-minute mean hold is met exactly, at the boundary.
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(s) x (open at T_P + 12 minus open at T_P + 2), in ticks, on
    traded days is positive.
  - **Descriptive split (not a trial):** the same statistic for |s| above and at-or-below the research
    window's median |s|, following P-K5-001-c's larger-move result.
- **Topstep check:**
  1. Flat by F: last fill 10:12 at the latest.
  2. Order type: market.
  3. D9.4: one trade a day, entered two minutes after a scheduled auction start, not a gapped release
     minute; no stops.
  4. Star rules: MGC per C6.
  5. News: no C11 release inside the window. <= 1 lot-equivalent.
  6. D9.5a: fills at T_P + 2 and T_P + 12 are outside [T_P, T_P + 2). If the lead confirms C11's auction
     row, both fills pay D8's largest-bucket cost (fills within 30 minutes after the start).
  7. CPI window: outside it.
  8. Caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the gold vehicle, research and confirmation windows. External: EC-LBMA,
  EC-UKBH, EC-CAL.
- **Trials in N:** 1.

### K5-fomc-01 (gold: continuation of the first five minutes after the FOMC statement)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source covers 2007-2020, overlapping the confirmation window.]
- **Cluster** K5. **Products read:** the gold vehicle; EC-FOMC; EC-CAL.
- **Traded exposure:** gold {GC, MGC}, only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed** (K5-024, Awartani, Hussain, Virk 2024; GC 5-minute data 2007-2020, P-K5-024-c):
    - "we find that the gold price adjustment and its volatility adjustment continue for longer than five
      minutes after the FOMC shock. This suggests potential short-term inefficiencies in the gold market
      concerning the short-term rates" (P-K5-024-a).
    - "positive monetary policy shocks tend to reduce the price of gold ... However, the adjustment 10
      minutes after the shock is significantly threefold higher than after 5 minutes" (P-K5-024-b).
    - "The gold returns and volatility 5 min after the shock are found to be more sensitive to looser than
      tighter FOMC rate announcement changes" (P-K5-024-a).
  - **The rule-3 route.** The source's surprise measure is not in the logged passages. A fed-funds-futures
    surprise would be a rates leg, which is K8's (section 4). The proxy is gold's own first five minutes.
  - **Reasoning.**
    - A tightening shock lowers gold (P-K5-024-b). When the shock dominates the first five minutes, the sign
      of gold's move over 13:00-13:05 CT is the sign of the gold response to the surprise.
    - The 10-minute adjustment is three times the 5-minute one, so the response continues in that
      direction between minutes 5 and 10.
    - The loosening/tightening asymmetry does not enter a sign rule.
  - **Counter-evidence in the log (other events).**
    - For 08:30 ET releases, gold's reaction is fast: "the majority of the reaction complete within 90-s"
      (K5-004, P-K5-004-a); "returning to normal within approximately 2½-min" (K5-019, P-K5-019-c).
    - Elder et al.: "the effect of macroeconomic news dissipates quickly, within about 60 minutes"
      (P-K5-014-d).
    - The source's "inefficiency" is not costed (log quality tells).
    - K5-030 (Gu, Kurov, Stan 2023, FOMC and commodity markets) was never read and is not used.
  - **Classification:** port of D.1 family E (FOMC event), tested on gold specifically (rule 6). New member.
    Not extended to silver, copper or platinum: the evidence is gold-only (the lead's 21:52 Q6 logic).
- **Entry rule.**
  - **Days:** eligible trade dates (C4) that are EC-FOMC statement days, statement at 13:00 CT.
  - **Signal:** s = close of the bar at 13:04 minus close of the bar at 12:59. Both bars must exist with one
    instrument_id.
  - **Order:** s > 0 BUY q_c; s < 0 SELL q_c; s = 0 no trade. Market intent on the bar at 13:04, filling at
    the open of the bar at 13:05.
- **Exit rule:** market intent on the bar at 13:14, filling at the open of the bar at 13:15.
- **Holding horizon:** 10 minutes. **Session window:** 13:05-13:15 CT. Flat 113 minutes before F.
- **Data fields read:**
  - Gold vehicle ohlcv-1m close and instrument_id at 12:59 and 13:04 (C8). Paid; available at 13:05.
  - EC-FOMC (C9). Free, 2019-2026, published before each year; release time verified per statement page.
  - EC-CAL.
- **Order type:** market. **Sizing:** q_c.
- **Parameters.**
  - **Signal of 5 minutes:** the source's "5 min after the shock" (P-K5-024-a).
  - **Entry at 13:05:** the start of the 5-to-10-minute continuation (P-K5-024-b).
  - **Exit at 13:15: a judgment.** It is D9.3's 10-minute minimum mean hold. The last five minutes
    (13:10-13:15) lie beyond the source's 10-minute horizon.
  - **Grid:** none.
- **Expected entries and hold:** 10 research events (C12), about 37-38 confirmation events. Held 10
  minutes. Floor ok (mean exactly 10). Power: probably "inconclusive by design" (D4); the lead's 21:52 Q4
  ruling keeps low-frequency event members for the power check to decide (section 7, item 4).
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(s) x (open at 13:15 minus open at 13:05), in ticks, is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 13:15.
  2. Order type: market.
  3. D9.4: one trade per meeting, entered five minutes after the statement, not in the release minute;
     no stops.
  4. Star rules: MGC per C6.
  5. News: the position opens after the release. <= 1 lot-equivalent.
  6. D9.5a: fills at 13:05 and 13:15 are outside [13:00, 13:02). Both are within 30 minutes after FOMC, so
     both pay D8's largest-bucket cost.
  7. CPI window: not applicable (13:05).
  8. Caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the gold vehicle, research and confirmation windows. External: EC-FOMC,
  EC-CAL.
- **Trials in N:** 1.

### K5-ovr-01 (hourly overreaction reversal)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP (same source and sample as K4-ovr-01, 2019-11-20 to 2020-06-03). K4-ovr-01 and K5-ovr-01 must carry one identical rule text (review R-24); E.1 checks it before hashing.]
- **Cluster** K5. **Products read:** each traded exposure's own vehicle; EC-CAL.
- **Traded exposures** (each a separate trial; each only if D2 admits it): gold, silver ~~, platinum~~ and copper [U2: platinum OUT].
  - These are the K5 exposures in the source's sample: "gold (GC), silver (SI), platinum (PL), palladium
    (PA), copper (HG)" (P-K5-029-b).
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed** (K5-029, Borgards, Czudaj, Hoang 2021, a panel source claimed by K5):
    - Large intraday price changes beyond a decile threshold, at 1-minute to 1-hour frequencies, are
      followed by reversals.
    - "soft and metal commodities show much less overreactions than precious metals and especially energy
      commodities" (P-K5-029-a).
    - "almost all commodities have higher trading returns with exception of industrial metals which have a
      0.98% lower but still positive return in the first decile" (P-K5-029-c).
    - "the metals index would have generated a 4.0% (5.0%) compounded return over the pandemic period after
      positive (negative) first decile overreactions for the 1-h frequency" (P-K5-029-c).
    - Costs are asserted, not modelled: "the net-of-fees trading results would be still positive in both
      periods" (P-K5-029-d).
  - **Why copper is included.** "Metal commodities" in P-K5-029-a are the industrial metals (copper,
    aluminium, zinc, nickel in P-K5-029-b), which show fewer overreactions than the precious metals. Their
    first-decile return is "lower but still positive" (P-K5-029-c). The lead may cut copper (section 7,
    item 5).
  - **Evidence quality.**
    - About six months of data, 2019-11-20 to 2020-06-03, dominated by Covid (P-K5-029-a).
    - The holding period and threshold construction are [unverified].
    - The per-commodity tables were not transcribed (log quality tells).
  - **Classification:** a family C magnitude-conditioned reversal, tested per commodity. D6 does not port
    family C, so under partition rule 6 this is a cluster member. K4-ovr-01 uses the same panel source for
    energy (its [K4] passages). The judgments below are made independently, and where they coincide with
    K4's the entry says so, so that the lead can keep the source tested the same way across clusters.
- **Decision times:** t = O + 60k for k = 1, 2, ... while t <= C (D6 rows). Gold and silver: 08:20, 09:20,
  10:20, 11:20, 12:20 (five). Copper: 08:10, 09:10, 10:10, 11:10 (four). ~~Platinum: 08:20, 09:20, 10:20,
  11:20 (four).~~ [U2: platinum OUT.]
- **Signal:** r(t) = (close of the bar at t - 1 minus open of the bar at t - 60) / open of the bar at t -
  60, the return over the hour [t - 60, t). Both bars must exist with one instrument_id.
- **Reference set and cuts.**
  - The reference set is the values r(tau) at the same decision clock times on the 20 most recent earlier
    eligible trade dates (C4) of the exposure.
  - At least 80% of the possible values must exist: 80 of 100 for gold and silver, 64 of 80 for copper and
    platinum. Otherwise no trade at t.
  - P10 and P90 = np.percentile(values, [10, 90], method="linear").
  - Warm-up: the first 20 eligible dates of each window. No bars before the research window exist, because
    holdout-2 is sealed.
- **Entry rule.**
  - r(t) <= P10: BUY q_c. r(t) >= P90: SELL q_c. Otherwise no trade.
  - Market intent on the bar at t - 1, filling at the open of the bar at t.
- **Exit rule:** market intent on the bar at t + 58, filling at the open of the bar at t + 59. At most one
  position is open. The next decision's entry fills at t + 60, so positions never overlap.
- **Holding horizon:** 59 minutes. **Session window:** gold and silver 08:20-13:19; copper 08:10-12:09;
  ~~platinum 08:20-12:19~~ [U2: platinum OUT]. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8), all closed at or before t, and
  earlier trade dates; EC-CAL. Paid; history 2019-05 on (MHG 2022-05, C8).
- **Order type:** market. **Sizing:** q_c.
- **Parameters.**
  - **60-minute signal and decile cuts:** the source's "1-h frequency" and "first decile" (P-K5-029-c). The
    symmetric cuts follow "positive (negative) first decile overreactions" (P-K5-029-c) and P-K5-029-d.
  - **20-trade-date trailing reference: a judgment.** It is the program's trailing-state length (D15.4 B4).
    The source's own threshold construction is not in the logged passages. This is the same length K4
    chose.
  - **59-minute hold: a judgment.** It is one signal period less the one minute that keeps positions from
    overlapping. The source's holding period is [unverified].
  - **Grid:** none.
- **Expected entries and hold:** by construction about 2 in 10 decision times qualify if the trailing
  distribution is stable. That is about 1 entry per day per exposure (at most 5), held 59 minutes. Floor ok.
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of -sign(r(t)) x (open at t + 59 minus open at t), in ticks, is
    positive. It is reported split by the sign of r(t).
- **Topstep check:**
  1. Flat by F: last fill 13:19.
  2. Order type: market.
  3. D9.4: at most 5 entries a day, 59-minute holds, no stops or brackets. The first decision (08:10 or
     08:20) fades an hour that contains the 07:30 releases, 40-50 minutes after them, not in a gapped
     minute.
  4. Star rules: C6.
  5. News: gold and silver 12:20 positions hold through the 13:00 FOMC statement; copper 08:10 positions
     hold through G.17 (08:15). <= 1 lot-equivalent.
  6. D9.5a: fills fall at :20 and :19 (gold, silver, platinum) or :10 and :09 (copper). None is in a
     guarded minute (07:30-07:31, 08:15-08:16, 13:00-13:01, or an auction start at 08:00-08:01,
     09:00-09:01 or 10:00-10:01). Two groups of fills pay D8's largest-bucket cost:
     - the gold and silver 13:19 exit on FOMC days;
     - if C11's auction row is confirmed, fills within 30 minutes after the exposure's own auction start:
       gold at 09:19-09:20 (10:19-10:20 in 5-hour weeks) and platinum at 08:20 (09:19-09:20 in 5-hour
       weeks).
  7. CPI window: the first fill is 08:10, outside it.
  8. Caps: C6. Platinum may be suspended.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of all ~~four~~ three [U2] admitted vehicles, research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 3 after U2; E.0: at most 4).

### K5-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: the 01:47 fallback ruling (gold, then silver, then copper) governs; this entry's "No fallback is declared" is superseded; KF1-KF3 and KF5 remain gold-event features whichever metal becomes the vehicle.]
- **Traded vehicle: the gold exposure** {GC, MGC}; the contract is chosen by D2 in E.2. [Lead ruling, 01:47 PDT, question 6: fallback order if D2 does not admit gold: silver, then copper; the features stay as written, reading silver bars (an IN exposure) whether or not silver is traded.]
  - **Reason 1, the log:** gold is the exposure the K5 log documents most at intraday horizons. Of the 31
    passed K5 items, gold is a product in 27 (all but K5-009, K5-010, K5-023 and K5-030 [unverified]),
    silver in 14, platinum in 7, and copper in 4 (5 with K3-007). Each count is from the item's "Products"
    line in the log.
  - **Reason 2, activity:** gold has the cluster's highest public ADV (MGC 429,702 contracts a day,
    2026 Jan-Aug, D1 table).
  - **Reason 3, caps:** gold is the only K5 exposure none of whose contracts can be set to zero under
    D9.11.
  - **No fallback is declared.** The cluster features below are gold-specific (gold auctions, gold FOMC
    evidence). If D2 admits no gold contract, the lead decides.
- **Products the features read:**
  - The gold vehicle.
  - The silver vehicle's bars, for KF6. D13 buys history only for each traded exposure's chosen vehicle,
    so E.2 must add silver bars (SIL, the most active silver contract) if silver is not admitted.
  - Calendars: EC-LBMA, EC-UKBH, EC-FOMC, EC-BLS, EC-CAL.
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12.
  - Throughout, t_j is the decision time, and "the bar at t_j - 1" is the last bar closed at t_j.
  - tick = 0.10 (GC and MGC alike, C7).
  - T_P(d) = T_CT(d, 15:00) and T_A(d) = T_CT(d, 10:30) (C10), defined on scheduled auction days (C9).

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | pm_minutes | If d is a scheduled gold PM auction day: t_j - T_P(d) in minutes (signed). Otherwise the literal 999 | K5-001 P-K5-001-a, P-K5-001-b; K5-012 P-K5-012-f, P-K5-012-g, P-K5-012-h, P-K5-012-i; K5-011 P-K5-011-f; K5-006 P-K5-006-f, P-K5-006-g | calendar and clock only; schedule known before d (C9) |
| KF2 | pm_open_move | If d is a PM auction day and t_j >= T_P + 2 min: (close of the bar at T_P + 1 - close of the bar at T_P - 1) / tick. Otherwise 0. On such a d with t_j >= T_P + 2, a missing bar or a change of instrument_id means no trade at t_j | K5-001 P-K5-001-a, P-K5-001-c, P-K5-001-g; K5-012 P-K5-012-h, P-K5-012-i (the K5-pmfix-01 signal) | T_P + 2 (close of the bar at T_P + 1) |
| KF3 | am_move | If d is a gold AM auction day: (close of the bar at T_A + 9 - close of the bar at T_A - 31) / tick, the move from 30 minutes before the AM auction to the end of its tenth minute. Otherwise 0. A missing bar or a change of instrument_id means no trade on d | K5-002 P-K5-002-a (pre-auction pressure outside US hours); K5-012 P-K5-012-h ("complete within ten minutes"); K5-001 P-K5-001-a | T_A + 10 = 04:40 or 05:40 CT, before W0 |
| KF4 | event_code | 0 = no event; 1 = d has an Employment Situation or CPI release at 07:30 CT (EC-BLS); 2 = d is an EC-FOMC statement day; 3 = both | K5-014 P-K5-014-a, P-K5-014-c, P-K5-014-d; K5-015 P-K5-015-a; K5-004 P-K5-004-c, P-K5-004-e; K5-019 P-K5-019-c; K5-024 P-K5-024-a | schedules known before d (C9; the schedule as published by the evening before d) |
| KF5 | fomc_move | If d is an EC-FOMC statement day and t_j >= 13:05: (close of the bar at 13:04 - close of the bar at 12:59) / tick. Otherwise 0. On such a d with t_j >= 13:05, a missing bar or a change of instrument_id means no trade at t_j | K5-024 P-K5-024-a, P-K5-024-b (the K5-fomc-01 signal) | 13:05 CT |
| KF6 | gs_ratio_dev | R(tau, d) = ln(close of the gold vehicle's bar at tau - 1 / close of the silver vehicle's bar at tau - 1), both in USD per troy ounce. Value = (R(t_j, d) - m) / s, where m and s (ddof = 1) are the mean and standard deviation of R at the same clock time t_j on the 20 most recent earlier eligible trade dates with both bars present. At least 16 values and s > 0 are required, else no trade at t_j. The 20-date z-score stands in for the source's "unexpected deviations", whose model is not logged: a judgment | K5-031 P-K5-031-a (valuation pressure from unexpected gold-silver ratio deviations predicts variance). R-K5-031's negative mean-reversion finding is why this is a feature and not a member (X-10) | bars closed at or before t_j |
| KF7 | ret60_pct | r60(tau) = (close of the gold vehicle's bar at tau - 1 - open of its bar at tau - 60) / tick. Value = (number of reference values < r60(t_j) + 0.5 x number equal) / number of reference values. The reference set is r60 at the 14 decision clock times on the 20 most recent earlier eligible trade dates, counting each value whose bars exist with one instrument_id. At least 224 values are required, else no trade at t_j | K5-029 P-K5-029-a, P-K5-029-c, P-K5-029-d (decile overreactions at the 1-hour frequency) | bars closed at or before t_j, and earlier trade dates |

- **Decision window [W0, W1] = [07:15, 13:45] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 07:15, 07:45, ..., 13:45, which is 14 a day. W1 + h = 14:15 <= F = 15:08.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 to the open of t_j + 30. Every
    fill therefore falls at :15, :16, :45 or :46.
  - **Why this window:** it spans every scheduled gold event the log documents inside the US day, each
    strictly inside a position interval and never at a fill:
    - the 07:30 CT Employment Situation and CPI releases, inside [07:16, 07:45];
    - the gold PM auction start, 09:00 CT inside [08:46, 09:15], or 10:00 CT in 5-hour weeks inside
      [09:46, 10:15];
    - the London/New York overlap, 2-4 pm London (Chai et al.: "the information share of London/New York is
      over two and half times of those of the rest of Europe and U.S.", P-K5-016-a);
    - the GC settlement period, 12:29-12:30 CT, inside [12:16, 12:45];
    - the 13:00 CT FOMC statement, inside [12:46, 13:15], with the fomc_move continuation in [13:16, 13:45].
  - **Consequences of the offset:**
    - No opening fill lands in the CPI window [07:25, 07:35]; entries are at 07:16 and 07:46. So D9.12 never
      binds, and MGC's 3-contract CPI cap is never reached.
    - No fill lands in any C11 minute.
  - **Why it starts at 07:15:** the first :15/:45 time before the 07:20 open lets the first position span
    the 07:30 releases. Its entry at 07:16 is four minutes before the day session (C14).
  - **The AM auctions (04:30 or 05:30 CT) are not decision times.** They enter as a feature (KF3); the
    pre-auction trade itself is K5-preauc-01.
  - **Why h = 30:** it is the scale on which the logged gold effects play out:
    - the post-reform auction completes "within ten minutes" (P-K5-012-h);
    - the FOMC adjustment continues past 5 and to 10 minutes (P-K5-024-b);
    - macro effects dissipate "within about 60 minutes" (P-K5-014-d);
    - K5-012's event window runs from 30 minutes before to 60 minutes after the fix start (log product
      line).

    h = 15 would split the release and auction responses into many costly intervals. h = 60 or 120 would
    fold the 07:30 releases, the PM auction and its aftermath, and FOMC with its continuation into single
    intervals. h = 30 keeps each event in its own interval.
- **Expected rows:** 14 x the eligible research-window trade dates. That is about 305 dates, less
  roll-blackout, vendor-degraded and early-halt dates (D15.3), less the 20-date warm-up of KF6, KF7 and B4:
  roughly 3,500-4,000 rows. E.2 gives the exact count.
- **Expected entries:** at most 14 per day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at >= 80%
  achieved null power on the confirmation window counts against it). Failing the D5 screen puts it in Tier
  B.
- **Topstep check:**
  1. Flat by F: last exit 14:15.
  2. Order type: market (D15.6).
  3. D9.4: at most 14 entries a day, 30-minute holds, no stops or brackets. No fill in a release or
     auction-start minute.
  4. Star rules: MGC at most 10 (C6). No opening fill in the CPI window, so the 3-contract cap never binds.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span a release.
  6. D9.5a: no fill in any C11 minute.
  7. CPI window: entries at 07:16 and 07:46, outside [07:25, 07:35].
  8. Caps: C6.
  9. Price limit: C13.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for every ML
    member.
- **Data needed:**
  - ohlcv-1m of the gold vehicle and the silver vehicle (or SIL, per above). The research window is used for
    training and tuning, the confirmation window for the frozen model.
  - Gold bars around the AM auction (03:59-05:40 CT) for KF3.
  - The member-level coverage check covers 07:16-14:15 (C14).
  - External: EC-LBMA, EC-UKBH, EC-FOMC, EC-BLS, EC-CAL.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K5-fixrev-01 | Fade the last two minutes of the gold fix: "the two minutes leading to the end of the fixing do show statistically significant negative returns ... overshoot" (K5-001 P-K5-001-g) | Rule 3 (timing); D9.3; rule 1 | The auction end is not scheduled: the benchmarks "do not have set publication times" (LBMA page, K5 log 3.0). Timing a rule on it would need each day's result timestamp, which is either read after the fact (look-ahead) or from a source whose licensing and history are unverified. A two-minute effect cannot meet the 10-minute mean hold. The evidence is from the old regime only. |
| X-02 K5-fixsil-01 (and gold AM / platinum variants) | K5-pmfix-01's continuation rule applied to the silver auction (06:00 or 07:00 CT), the gold AM auction or the platinum auctions | Rule 1 (evidence) | Silver shows "a significant decline in cumulative adjusted returns" after the reform (P-K5-012-e), which is evidence against. Caminschi tests the PM gold fixing only (P-K5-001-b, P-K5-001-d). The post-reform gold and platinum results are insignificant (P-K5-012-e). The seed test is written once, as K5-pmfix-01. |
| X-03 K5-relsurp-01 | A post-release trade on GC, SI or HG signed by the consensus surprise of NFP, CPI, GDP, durable goods or industrial production (K5-014 P-K5-014-a, P-K5-014-c; K5-015 P-K5-015-a; K5-018 via P-K5-014-f; K5-004 P-K5-004-b) | Rule 3 (proprietary consensus); contemporaneous; D9.4 and D9.5a | Consensus surveys are proprietary, and no named, obtainable history is in the log. With a price proxy nothing is left to trade: "the majority of the reaction complete within 90-s" (P-K5-004-a); volatility and returns normal "within approximately 2½-min" (P-K5-019-c). A release-minute fill is the gapped-market case the guard exists for. The releases enter only as C11's cost and guard list and as the ML feature event_code. |
| X-04 K5-dispersion-01 | Gold's release response conditioned on analyst belief dispersion (K5-004, title and P-K5-004-a context) | Rule 3 | Analyst-level forecast dispersion is proprietary; no obtainable history is named. |
| X-05 K5-liqwd-01 | Trade the liquidity withdrawal and recovery around monetary-policy announcements: "liquidity is removed from the market around 5-minutes prior to the announcement and reverts to normal within 10-minutes (gold market) and 20-minutes (silver market)" (K5-005 P-K5-005-a) | Brief rule 13 (lead ruling) | The paper conditions on investor sentiment. The lead ruled K5-005 excluded (reports/stage_e0_STATE.md, 3-K5b row). The log notes that the liquidity timing itself does not need sentiment; the ruling stands, and the question is not reopened here. |
| X-06 K5-chpmi-01 | HG or SI traded on the Chinese PMI: "coefficient estimates of 0.18 and 0.06 for copper and silver, respectively" (K3-007 P-K3-007-h [K5]) | Rule 3; rule 1 | It is a surprise response against a proprietary consensus. With a price proxy nothing is left: the K3 log records the impact "appears to be permanent" (first-run passage, not re-checked), and the response lies inside a 20-minute window at US night (P-K3-007-c). The pre-announcement CARs are "available upon request" (P-K3-007-g, [K3] only). |
| X-07 K5-abnret-01 | Gold momentum after an intraday-detected abnormal daily return, and next-day gold contrarian (K5-028 P-K5-028-a, P-K5-028-d, P-K5-028-e, P-K5-028-f) | Rule 1 (parameters; evidence) | The abnormal-return threshold is not in the logged passages; only gold's timing is ("after 5 p.m. ... after 7 p.m.", GMT+3 clock, P-K5-028-d). The data are MetaQuotes broker prices with no named instrument (P-K5-028-b), and there are no costs (P-K5-028-c). The simulated exit at the GMT+3 day end is 16:00 CDT in summer, after F. The gold contrarian leg is "Not rejected", no better than random (P-K5-028-e, P-K5-028-f). The same-day continuation is **covered by CP1** in its unconditional form. |
| X-08 K5-rsi-01 / K5-kc-01 | RSI reversal on 1-minute bars, and a 60-minute Keltner-channel breakout with "1.5 Average True rang Multiplier", on GC, SI, PL, HG (K5-008 P-K5-008-a, P-K5-008-b) | Rule 1 (parameters; evidence quality) | The RSI length and cut levels and the channel's average and ATR lengths are not in the retrieved text. Whether positions are held overnight is [unverified]. Parameters were optimized by PSO over one 21-month window (P-K5-008-c) with no out-of-sample test seen, and the text read was abstract plus snippets. These are D.1 families C and G, which D6 does not port, and no product-specific parameter can be traced. |
| X-09 K5-tokfade-01 | Fade the Tokyo-session move of GC or PL during the New York session, reasoning that "uninformed trading is more prevalent during the Tokyo day session while informed trading dominates the New York day session" (K5-025 P-K5-025-a) | Rule 1 (no directional claim) | The passage is descriptive (abstract only). The reversal is this writer's inference, not a tested claim. It would also bet against CP1's overnight-continuation form without evidence. |
| X-10 K5-gsratio-01 | Gold-silver ratio (spread) mean reversion, intraday | Rule 1 (evidence against); D2 | K5-031 predicts variance, not direction (P-K5-031-a). R-K5-031 (Batten, Ciner, Lucey) is negative: "limited opportunity to profit from strategies based on mean reversion of the spread". R-K5-034 has no intraday horizon. A two-leg member would also need D2's parity sizing across a starred SIL leg capped at 2 contracts. The ratio enters K5-ml-01 as KF6 only. |
| X-11 K5-shfe-01 | GC or SI traded on an SHFE night-session lead (K5-020) | Rule 1 (evidence against); data | The evidence says COMEX leads: SHFE gold's price-discovery share "falls relative to the United States", and spillovers grow "particularly from the United States to China" (P-K5-020-c, P-K5-020-d). No free intraday SHFE history for 2019-2026 is named in the log. |
| X-12 K5-efp-01 | Trade GC on reversion of the futures-minus-spot EFP spread (K5-032 P-K5-032-a, P-K5-032-b) | Tradability; data | It needs the OTC spot leg, which the account cannot trade and the data plan does not hold. Direct arbitrage is rare because "one would have to cross two spreads" (P-K5-032-c). |
| X-13 K5-idxroll-01 | GC or HG around the S&P GSCI roll, 5th-9th business day (K4-034 P-K4-034-b, P-K4-034-c [K5]; K4-035 P-K4-035-b, P-K4-035-c [K5]) | Flat by F; rule 1 | As documented, the effect is a multi-day nearby-minus-deferred differential or a 1-3-week calendar spread, which breaks the 15:08 flat rule and is not an exposure's D2 vehicle. The pooled effect "is of 17 basis points at most" and "never significant" after standard-error adjustment (P-K4-034-a). K4-036 has no metals. A single-leg intraday version has no passage. |
| X-14 K5-ip-01 | HG traded on the 09:15 ET industrial production release (P-K5-014-c) | Rule 3; contemporaneous | This is the copper case of X-03. The release enters only C11's copper cost and guard list. |
| X-15 K5-open-01 | Trade the day-session open (07:20 CT) jump in volume and volatility (P-K5-004-f; P-K5-019-c "A spike in market activity of a lower magnitude is also registered as the trading pit opens") | Rule 1; D6 | The claim is descriptive and dates from the pit era. It is a family A session-clock effect, which D6 does not port. After COMEX's move to Globex "the price discovery shares remain relatively stable throughout the day" (P-K5-011-d). |
| X-16 K5-fixvol-01 | A daily-bar volatility regime member built on the 2014-2015 fix change (K5-006) | Not intraday-feasible; rule 1 | Crain et al. is a daily structural-break study (P-K5-006-b). Its raw and trend-controlled results point opposite ways (P-K5-006-c against P-K5-006-f and P-K5-006-g), and both are stated in K5-pmfix-01. |
| X-17 K5-fomc-ext-01 | K5-fomc-01 extended to silver, copper or platinum | Rule 1 (no evidence) | K5-024 tests gold only. Following the lead's 21:52 ruling Q6 (no extension without logged evidence), not written. It would cost up to 3 trials. |

---

## 3. Beyond budget (lead decides)

None. The log supports 4 new members inside the budget of 11. These candidates were considered and not
written; none is a budget overflow:
- **A post-auction recovery leg for K5-preauc-01** (long from T to T + 30). P-K5-012-g's "steady recovery"
  of depth suggests it, but no passage claims a price reversal after the start. Not written.
- **A size-thresholded K5-pmfix-01** (trade only when |s| is large). This would follow P-K5-001-c's 80-95%
  for larger moves, but no threshold value is logged. The split is reported descriptively instead.
- **The X-02 and X-17 extensions**, which have no evidence (section 2).

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Multiple sources (not pinned), K5 log section 4 | gold (K5); dollar and real rates (K3, K2) | the dollar-and-gold relationship (partition section 3) |
| Wright Blogs, "Metals as Macro Signals ..." (not read) | metals (K5); macro and cross-asset (K1, K2, K3) | metals as a cross-asset signal |
| Baur and Kuck (2019), FRL, "The timing of the flight to gold ..." (SSRN 3243111) | gold (K5); S&P 500 (K1) | intraday flight-to-safety timing |
| "Effects of idiosyncratic jumps and co-jumps on oil, gold, and copper markets" (Energy Economics 2021, 10.1016/j.eneco.2021.105660) | oil (K4); gold and copper (K5) | one-minute co-jumps across commodities |
| arXiv 2409.08355, copper and S&P 500 dynamic correlations | copper (K5); S&P 500 (K1) | low-frequency equities-against-copper |
| Quantpedia, "Cross-asset price-based regimes for gold" (not read) | gold (K5); other clusters | cross-asset regime signal |
| JFM 2025, "Gold Jump Risk, Rare Macroeconomic Disaster Probability, and Expected Stock Returns" (10.1002/fut.70074) | gold (K5); equities (K1) | gold jumps predicting stock returns |
| K5-024's FOMC rate surprise, if measured from fed funds futures (this catalog) | rates surprise (K2); gold (K5) | a surprise-signed gold FOMC trade needs a rates instrument; K5-fomc-01 uses gold's own response instead |

The first seven rows are the reader's own flags (K5 log section 4). The last row is this catalog's
routing. Other clusters' logs also flag gold or copper legs (K1 log line 527; K7 log lines 747-757); those
are theirs to route.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K5.md section 3, and every `[K5]`-tagged
passage or registry tag elsewhere.

| Item | Disposition |
|---|---|
| 3.0 timing facts (LBMA and IBA times, LME and SHFE hours, CME settlement windows, Globex hours) | Used: C3, C5, C9, C10; K5-preauc-01, K5-pmfix-01, K5-ml-01. SHFE and LME hours are background only (X-11; no copper Asian-session source passed) |
| K5-001 Caminschi, Heaney | Used: K5-pmfix-01 (P-a, b, c, f, g); K5-ml-01 KF1, KF2, KF3. The end-of-fix reversal is excluded, X-01 |
| K5-002 Nilsson | Used: K5-preauc-01 (P-a); K5-ml-01 KF3 |
| K5-003 | Duplicate of K5-006 (log) |
| K5-004 Smales, Yang | Used as counter-evidence in K5-fomc-01 (P-a) and in K5-ml-01 KF4 (P-c, P-e). The surprise-signed trade is excluded, X-03; the dispersion member is excluded, X-04. The pit-open fact (P-f) is excluded, X-15 |
| K5-005 Smales, Lucey | Excluded, X-05 (lead ruling, sentiment) |
| K5-006 Crain, Hoelscher, Jones | Both sides stated in K5-pmfix-01 (P-c against P-f and P-g); K5-ml-01 KF1. As a member it is not intraday-feasible, X-16 |
| K5-007 Batten et al. (stylized facts) | Insufficient evidence for a member: descriptive periodicity (P-a) of spot metals, family A, which D6 does not port. Not used |
| K5-008 Cohen | Excluded, X-08 |
| K5-009 Wang, Lu | Insufficient evidence: a volatility-forecasting comparison with no trading claim (P-a). Not used; B4 carries volatility state in the ML member |
| K5-010 LBMA silver FAQ | Used for auction mechanics and timing (C9, C10; K5-preauc-01's silver leg) |
| K5-011 Hauptfleisch, Putnins, Lucey | Used: K5-pmfix-01 context and K5-ml-01 KF1 (P-f, noise around the fix). P-d is used in X-15. Otherwise descriptive price-discovery shares: insufficient evidence for a member |
| K5-012 Aspris, Foley, Gratton, O'Neill | Used: K5-pmfix-01 (P-a, d, e, h, i); K5-preauc-01 (P-f, P-g, and the log's window line); K5-ml-01 KF1, KF2, KF3 and the h choice. Silver and other auction variants are excluded, X-02 |
| K5-013 Aspris, Foley, O'Neill | Used as counter-evidence in K5-pmfix-01 (P-a) |
| K5-014 Elder, Miao, Ramchander | Used: C11 (P-a, P-c); K5-fomc-01 counter-evidence (P-d); K5-ml-01 KF4 and the h choice. Surprise members are excluded, X-03 and X-14 |
| K5-015 Cai, Cheung, Wong | Used: C11 (CPI, P-a); K5-ml-01 KF4. The surprise member is excluded, X-03 |
| K5-016 Chai, Lee, Wang | Used only for K5-ml-01's window placement (P-a). Descriptive shares: insufficient evidence for a member (family A) |
| K5-017 Sobti, Sehgal, Ilango | Insufficient evidence: descriptive price discovery (P-a), abstract only. Not used |
| K5-018 Christie-David, Chaudhry, Koch | Insufficient evidence: retrieval failed, secondary description only (P-K5-014-f). Its topic is covered by X-03 |
| K5-019 Smales | Used as counter-evidence in K5-fomc-01 (P-c); K5-ml-01 KF4; K5-preauc-01 (P-b, the floor-open clock). The pit-open fact is excluded, X-15 |
| K5-020 Jiang, Kellard, Liu | Excluded, X-11. P-a is used in K5-preauc-01 (the COMEX floor-open clock) |
| K5-021 Sehgal, Sobti, Diesting | Insufficient evidence: descriptive (P-a), abstract only. Not used |
| K5-022 Lauterbach, Monroe | Insufficient evidence: retrieval failed, title only |
| K5-023 Martell, Trevino | Insufficient evidence: retrieval failed, title only (K6's duplicate claim K6-005 points here) |
| K5-024 Awartani, Hussain, Virk | Used: K5-fomc-01 (P-a, b, c); K5-ml-01 KF4, KF5 and the h choice. The rates-surprise variant is routed to K8 (section 4); extensions are excluded, X-17 |
| K5-025 Iwatsubo, Watkins, Xu | Excluded, X-09 |
| K5-026 Batten, Lucey, Peat | Insufficient evidence: retrieval failed, title only |
| K5-027 Sobti | Insufficient evidence: retrieval failed, title only |
| K5-028 Caporale, Plastun ([K5] passages) | Same-day continuation **covered by CP1**; the threshold member and the next-day contrarian are excluded, X-07. The [K4] passages are K4's |
| K5-029 Borgards, Czudaj, Hoang ([K5] passages) | Used: K5-ovr-01 (P-a, b, c, d); K5-ml-01 KF7. The [K4] and [K6] passages are those writers' |
| K5-030 Gu, Kurov, Stan | Not used (never read; brief rule 13). Noted in K5-fomc-01 as unread |
| K5-031 Lyocsa, Todorova, Zhu | Excluded as a member, X-10. Used in K5-ml-01 KF6 (P-a) |
| K5-032 Barzykin, Bergault, Gueant | Excluded, X-12 |
| K3-007 [K5] Baum, Kurov, Wolfe, P-K3-007-h | Excluded, X-06 |
| K3-040 (registry tag K5; title only) Kosowski et al., "Overnight-Intraday Reversal Everywhere" | Insufficient evidence: content [unverified]. Note that CP1's (a) form bets the opposite way, overnight continuation |
| K4-034 [K5] Dubois, Maréchal | Excluded, X-13 (P-a null; P-b roll days; P-c constituents) |
| K4-035 [K5] Mou | Excluded, X-13 (multi-day spread, P-b; metals sector figures not extracted, P-c) |
| K4-036 (registry tag K5) Stoll, Whaley | No [K5] passage: "[K5] none (no metals in the roll tests)" (K4 log). Not used |
| K4-039 (registry tag K5) Brunetti, Reiffen | Rejected by K4 (R-K4-040), no [K5] passage. Not used |
| `[K5]` search in the K1, K2, K6, K7 logs and the K3 and K4 partial logs | No further [K5]-tagged passage. The K3 sonnet partial log's K3-007 tags are superseded by the K3 log. The K1 and K7 mentions are those readers' own K8 flags or rejections |
| R-K5-001 to R-K5-053 | Rejected at pre-filter or on reading. Not used. R-K5-018 (Rosa) is family CP1; R-K5-031 and R-K5-034 inform X-10; R-K5-046 (Kinlay GDX, "has recently begun to fail") is an ETF, not a K5 product |

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all four admitted) |
|---|---|---|---|
| K5-cp1-01 | gold, silver, copper ~~, platinum~~ [U2] | 1 | 3 (E.0: 4) |
| K5-cp2-01 | gold, silver, copper ~~, platinum~~ [U2] | 1 | 3 (E.0: 4) |
| K5-cp3-01 | gold, silver, copper ~~, platinum~~ [U2] | 1 | 3 (E.0: 4) |
| K5-preauc-01 | gold (AM), silver (platinum removed by the lead) | 1 | 2 |
| K5-pmfix-01 | gold | 1 | 1 |
| K5-fomc-01 | gold | 1 | 1 |
| K5-ovr-01 | gold, silver ~~, platinum~~ [U2], copper | 1 | 3 (E.0: 4) |
| ~~K5-ml-01~~ [excluded, U6] | gold (fallback silver, then copper: lead ruling) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | ~~**22** = 12 port + 9 new + 1 ML. In general 4E + 3a_G + a_S + a_P + 1. Without platinum: 17. Gold only: 8~~ [E.1: U9 (R-28) corrects the E.0 figure to 21 after the 01:47 ruling; after U2 and U6: **16** = 9 port + 7 new. In general 4E + 3a_G + a_S. Gold only: 7] |

The "without platinum" figure: 3 x 3 ports + 3 ovr + 2 preauc + 1 pmfix + 1 fomc + 1 ML = 17.
[E.1: with platinum OUT (U2) and K5-ml-01 excluded (U6): 9 + 3 + 2 + 1 + 1 = 16.]

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **Do LBMA auction starts count as "scheduled major releases"?**
   - C11 names each exposure's own auction starts for D8's event-window cost. That is conservative, and it
     raises the cost of K5-pmfix-01's two fills and of any port or K5-ovr-01 fill within 30 minutes after
     an auction start.
   - Whether auction starts also count for the D9.5a fill guard is the lead's call.
   - Every new member and the ML member are timed so that their fills never land in [T, T + 2), so the
     answer changes only the ports' fills (CP2 entries at 09:00-09:01 or 10:00-10:01 on gold, 08:00 or
     09:00 on platinum).
2. **C11's named releases.** Named: Employment Situation, CPI, FOMC, and G.17 for copper. Durable goods
   (08:30 ET) is also among Elder's largest-impact releases for gold and silver (P-K5-014-a), but its
   schedule source was not confirmed (census.gov 404). Should E.2 source it and add it?
3. **K5-preauc-01 rests on one abstract** (a practitioner SSRN paper, window and magnitude unverified).
   - It costs 3 trials. [E.1, U9 (review R-28): 2 trials after the 01:47 ruling.]
   - Platinum's window (03:15-03:44 CT, or 04:15-04:44 in 5-hour weeks) is the likeliest to fail the
     member-level coverage check (C14).
   - The lead may cut it, or keep gold and silver only.
4. **Low-frequency member.** K5-fomc-01 has 10 research and about 37-38 confirmation events. By arithmetic
   it needs about 30 x eps_X per event, so it is likely "inconclusive by design" (D4). It is kept under the
   21:52 Q4 ruling; the power check decides.
5. **K5-ovr-01 on copper.** The source reports fewer overreactions in industrial metals, with a "lower but
   still positive" return (P-K5-029-a, P-K5-029-c). Copper is included as a tested sample member (1
   trial).
   - The trailing-reference length (20 dates) and the 59-minute hold match K4-ovr-01's judgments for the
     same panel source.
   - If K6 writes the same source, the lead may want one rule text for all three clusters.
6. **K5-pmfix-01's post-reform evidence leans against it** (P-K5-012-a, P-K5-012-i; P-K5-013-a). It is kept
   as the partition's seed test (1 trial), with both sides stated, including Crain's daily results (P-K5-006-c
   against P-K5-006-f and P-K5-006-g).
7. **K5-ml-01 has no fallback exposure.** Its features are gold-specific. It also needs silver bars (KF6)
   even if silver is not admitted, which E.2 must add to D13's purchase.
8. **Platinum.** [Decided by the user, U2, 2026-09-24: platinum is OUT.]
   - PL has no micro and "Platinum (PL) = 0" is possible at Topstep's discretion (D9.11). Every platinum
     trial carries the "may be suspended" flag.
   - Platinum carries 3 ports + K5-preauc-01 + K5-ovr-01 = 5 trials.
   - Whether an exposure that can be switched off mid-program should carry trials at all is a user or lead
     decision (the "without platinum" total is 17).
9. **E.2 checks named in this catalog:**
   - (a) the platinum auction times for 2019-2021, when the LME administered the price, and any
     advance-announced UK half-days or special auction schedules (C9);
   - (b) the SI (12:25) and PL (12:05) settlement times behind D6's C (C5);
   - (c) the metals futures Globex hours (C3);
   - (d) the tick-size history 2019-2026 (C7);
   - (e) COMEX and NYMEX metals price limits or dynamic circuit breakers against Topstep's 2% rule (C13);
   - (f) member-level coverage for 03:15-06:59 CT (K5-preauc-01) and 07:16-07:20 (K5-ml-01) (C14);
   - (g) D8 slippage buckets for 03:00-07:00 CT (K5-preauc-01);
   - (h) MHG's short history and the HG price-path declaration (C8);
   - (i) EC-BLS from yearly Wayback captures, EC-FOMC statement times, EC-G17 dates (C9).
10. **Region gaps.** The partition asked K5 to read the COMEX settlement window, options expiry, the roll
    and delivery period, and copper's Asian session. The log found no passing source on any of them, so
    there is no member. No log item gives a copper-specific intraday mechanism other than K5-029's
    reversal and Elder's contemporaneous 09:15 response.
11. **Registry hygiene** (already noted by the reader, not rewritten): K5-004's DOI should be
    10.1016/j.irfa.2015.01.017; K5-005's should be 10.1016/j.intfin.2018.12.003; K5-003 duplicates K5-006.
    The registry also tags K4-036 and K4-039 with K5, but neither has a [K5] passage.

---

# Cluster K6

# Stage E.0 hypothesis catalog, cluster K6 (agriculture and livestock: ZC, ZW, ZS, ZM, ZL, HE, LE)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K6-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials.
> **K6 after the decisions: 7 active members, 27 confirmation trials** (4 new + 3 core ports (K6-ovr-01 excluded by the lead); 21 port + 6 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K6-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:29 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K6 product existed on this machine. The only product-specific numbers it uses are:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- calendar metadata (USDA release dates and clock times) and CME's price-limit rules as text (the
  limit levels in P-K6-047-a are rule parameters, not prices).

No price level, range or volatility of any K6 product is used or assumed below. Two logged passages
describe a single date inside the confirmation window: the August 12, 2019 corn report day,
P-K6-011-b and P-K6-011-e. They are cited only as illustrations of the D9.7 risk, and no parameter
is taken from them.

**Inputs read in full:**
- reports/stage_e0_research_K6.md.
- Every `[K6]`-tagged passage elsewhere: K3-007 (P-K3-007-j) and K3-040 (title only) in
  reports/stage_e0_research_K3.md; K4-034, K4-035 and K4-036 (and the R-K4-040 and R-K4-063 rows) in
  reports/stage_e0_research_K4.md; K5-023, K5-029 and K5-030 in reports/stage_e0_research_K5.md.
- reports/stage_e0_source_registry.jsonl: K6 lines and every line tagged K6.
- docs/STAGE_E_DESIGN.md: D1 to D15, including the 21:12 and 21:52 amendments recorded in
  reports/stage_e0_STATE.md.
- reports/stage_e0_partition.md, reports/stage_e0_topstep_facts.md, and the K6 rows of
  reports/stage_e0_liquidity.json.
- reports/stage_d1f_confirmation_list.md 2.1 A3 (Family H mechanics).
- reports/stage_e0_catalog_K4.md and reports/stage_e0_catalog_K2.md, for format only.

**Official pages fetched in this task.** These were fetched with curl on 2026-09-24 between 01:33 and
01:36 PDT, only to confirm that a data source exists and has history. No mechanism research was done.
Files are saved under the session scratchpad at fetch/k6cat.
- https://usda.library.cornell.edu/concern/publications/3t945q76s redirects (301) to
  https://esmis.nal.usda.gov/publication/world-agricultural-supply-and-demand-estimates (HTTP 200).
  - It lists dated WASDE releases with pdf, txt, xls and xml files. The month index runs back past 2018.
  - The index shows "December 2025 November 2025 September 2025": no October 2025 release is listed.
- https://usda.library.cornell.edu/concern/publications/8336h188j redirects (301) to
  https://esmis.nal.usda.gov/publication/crop-progress (HTTP 200).
  - It lists dated weekly releases (pdf, txt) for April to November of each year, back past 2017.
  - No October 2025 entry is listed.
- https://esmis.nal.usda.gov/publication/grain-stocks, /crop-production, /acreage and
  /prospective-plantings (HTTP 200 each). Each lists dated releases back past 2019. The latest
  releases shown are Grain Stocks Jun 30 2026, Crop Production Sep 11 2026, Acreage Jun 30 2026 and
  Prospective Plantings Mar 31 2026.

---

## 0. Header

| Item | Value |
|---|---|
| Exposures | corn {ZC}, wheat {ZW}, soybeans {ZS}, soybean meal {ZM}, soybean oil {ZL}, lean hogs {HE}, live cattle {LE}. One contract each; there are no Topstep-permitted micros (Topstep F1 lists only these seven K6 contracts) |
| D1 | **D1 applied: all seven K6 exposures IN; no starred product.** 2026 Jan-Aug ADV: ZC 505,663; ZW 180,405; ZS 302,997; ZM 181,637; ZL 232,819; HE 67,267; LE 68,652. Day-session coverage 0.990 to 1.000 (design D1 table). No K6 product appears in the D9.11 volatility caps or the D9.12 CPI window |
| D2 | Each exposure has exactly one admissible contract, so D2 has no vehicle choice. It either admits the contract (rho <= 2.0 at q = 1) or drops the exposure. An admitted exposure with rho < 0.5 trades at q = 1 and is flagged "undersized". Every entry reads "Vehicle: D2 (chosen in E.2)", and every trial is **traded only if D2 admits the exposure** |
| Members | **9 = 5 new + 3 core ports + 1 ML member.** Budget 15, so 6 slots are unused (section 3) |
| Trials in N (confirmation) | **39 if D2 admits all seven:** 21 port + 17 new + 1 ML. In general: 4E + (a_ZS + a_ZM + a_ZL) + (a_ZC + a_ZS) + a_ZC + (a_ZW + a_ZC + a_ZS + a_ZL) + a_ZC, where E is the number of admitted exposures and a_X = 1 if X is admitted |
| ML grid | ~~48 configurations, counted only in the K6 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Sizing | q = 1 contract in every member, which is 1 lot-equivalent: the D9.5 cap, half the 50K XFA's 2-lot maximum |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.**
  - Times are America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event (its open)
    is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values are usable from
    then on.
  - USDA releases published at "12:00pm ET" are 11:00 CT all year (P-K6-049-a: "11:00 a.m. CT (12:00
    p.m. ET)"), because both zones change clocks on the same dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open, as in D6 and D15.3.
  "Market intent on the bar at X" fills at the open of the bar at X + 1 min. Harness rules D9.5a
  (event-minute guard) and D9.7 (price-limit proximity) override a fill where they apply.
- **C3 Trade date.**
  - The program window for trade date d is [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md).
  - **Grains (ZC, ZW, ZS, ZM, ZL).** Trade date d opens with the evening session before d (19:00 CT;
    Sunday evening for a Monday) and ends at the 13:20 CT close on d. Between them is the 07:45-08:30
    CT pause (Topstep F4: "CBOT Commodity Market Pause (Mon-Fri): 7:45 AM - 8:30 AM CT. No orders
    accepted during this window"). The "trade date's first bar" is the first bar at or after that
    19:00 CT open. O = 08:30, C = 13:15, F = 13:18 (D6 table).
  - **Livestock (HE, LE).** Trade date d is the day session 08:30-13:05 CT only. The night session was
    cancelled in October 2014 (P-K6-023-d), and Topstep lists "Monday-Friday: 8:30 AM - 1:05 PM CT". The
    first bar is the 08:30 bar. O = 08:30, C = 13:00, F = 13:03 (D6 table).
- **C4 Exclusions for the five new members.** The ports follow D6 as written. A new member does not
  trade on:
  - roll-blackout dates (`screen_candidate` with `roll_blackout`);
  - dates the D10 grain or livestock calendar marks as early close or early halt ("Days with
    early_halt_ct set: no trade", Family H);
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which bars that one
    computation reads carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar, with the engine's
  forced flatten at F as the backstop. A lock at the daily limit shows up as bars at one price, and
  D9.7 governs it (C13).
- **C5 Flat time.**
  - F = 13:18 CT for grains and 13:03 CT for livestock. On early-close days F is the early close minus
    15 minutes (D9.1, D10).
  - No member holds any position across the 07:45-08:30 grain pause or overnight. The only overnight
    input any member reads is CP1's open of the 19:00 CT bar.
  - Every new member's last fill is at or before 13:14 (grains) or 12:59 (livestock).
- **C6 Size.**
  - q = 1 contract of the exposure's single admissible contract. That is 1 lot-equivalent ("minis 1",
    D9.6) and the D9.5 member cap.
  - No member sizes by signal, and no member holds two legs (section 2, X-01 and X-02).
- **C7 Ticks and fees.** Ticks are from reports/stage_e0_liquidity.json (CME specifications, fetched
  2026-09-23 20:49 PDT). Round turns are Topstep F3. The only fee change D8 applies (from 2026-10-01)
  is to MCL and MNG, not K6.

  | Contract | Tick | Tick value | CP2 buffer (4 ticks) | Topstep round turn |
  |---|---|---|---|---|
  | ZC | 0.0025 USD/bu (1/4 cent) | $12.50 | 0.01 USD/bu ($50) | $5.28 |
  | ZW | 0.0025 USD/bu | $12.50 | 0.01 USD/bu ($50) | $5.28 |
  | ZS | 0.0025 USD/bu | $12.50 | 0.01 USD/bu ($50) | $5.28 |
  | ZM | 0.10 USD/short ton | $10.00 | 0.40 USD/short ton ($40) | $5.28 |
  | ZL | 0.0001 USD/lb (0.01 cent) | $6.00 | 0.0004 USD/lb ($24) | $5.28 |
  | HE | 0.00025 USD/lb | $10.00 | 0.001 USD/lb ($40) | $5.22 |
  | LE | 0.00025 USD/lb | $10.00 | 0.001 USD/lb ($40) | $5.22 |

  These are 2026 specifications. E.2 confirms that each tick was unchanged over 2019-05..2026-06
  before any bar is read, because CP2's buffer, the ML features and several sign checks are in ticks.
  E.2 also confirms each product's raw price units in GLBX.MDP3 (cents or dollars per unit), which
  K6-crushgap-01's GPM needs.
- **C8 Price data.**
  - Source: Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is bought in
    E.1, and the confirmation and holdout-2 history of each admitted vehicle in E.2b (D13; K6 about
    $5.32 + $26.52 + $0.77 mbp-1).
  - History: all seven contracts have history from 2019-05. None is a micro with a late listing.
  - **Legs of non-admitted exposures.** If an exposure is not admitted by D2, D13 does not buy its
    history. E.2 must buy it as a leg where a member reads it: ZS, ZM and ZL for K6-crushgap-01; ZS
    for K6-ml-01.
  - Availability: a bar is available at its close (C1).
  - mbp-1 enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C9 Event calendars.** All are external and free. A rule reads only dates and scheduled clock
  times, except K6-ml-01's feature cp_ge_chg, which reads a published USDA value (C9d).
  - **(a) EC-USDA: the scheduled 11:00 CT grain releases.**
    - Covered releases: WASDE and Crop Production, which share a date (P-K6-038-b dates against
      P-K6-040-a "CropProduction1 / 12 10 10 9 12 11 10 12 11 9 10 10"); Grain Stocks; Prospective
      Plantings; Acreage.
    - Times:
      - "2026 WASDE Release Dates (12:00pm ET)" (P-K6-038-a);
      - "1 / Noonrelease" for Crop Production, Grain Stocks and Prospective Plantings (P-K6-040-a,
        P-K6-040-b);
      - WASDE "11:00 a.m. CT (12:00 p.m. ET)" (P-K6-049-a) and Grain Stocks "at 11:00 a.m. CT"
        (P-K6-049-c);
      - releases have been at 12:00 ET since January 2013, so throughout 2019-2026 (P-K6-012-b,
        P-K6-017-b, P-K6-018-b, P-K6-037-b).
    - Schedule sources: the USDA OCE WASDE page (yearly lists, Wayback captures for 2019-2025) and
      the NASS PFEI schedule PDF for each year (the 2026 one is K6-040; E.2 retrieves 2019-2025
      through Wayback).
    - Actual releases: the ESMIS record (esmis.nal.usda.gov, fetched above).
    - **Drop rule.** An event whose actual ESMIS date differs from the year's published schedule is
      kept only if a USDA notice of the new date, dated before d, is found. Otherwise it is dropped.
      ESMIS lists no October 2025 WASDE or Crop Progress, which E.2 must expect as gaps.
    - Subset **EC-WASDE**: the WASDE dates.
    - Notation: T = 11:00 CT on an EC-USDA date.
  - **(b) EC-CAL.** The D10 grain and livestock calendars (trade dates, holidays, early closes and
    halts, session hours), built by E.2 from CME schedules.
  - **(c) EC-FOMC.** No member reads it. It is used only by the harness for D9.5a and D8's event
    window, because Topstep lists "FOMC Statement | 1:00 PM | All products" (F6).
  - **(d) EC-CP: NASS Crop Progress, weekly.**
    - Timing: "4:00 pm ET - Crop Progress" on Mondays (P-K6-039-a), that is "3:00 p.m. CT (4:00 p.m. ET)
      on the first business day of each week, April through November" (P-K6-049-b).
    - Source: ESMIS dated txt and pdf releases, back past 2017 (fetched above).
    - Used only by K6-ml-01 cp_ge_chg.
- **C10 EC-LIM: settlements and price limits.** D9.7 needs these for every K6 member, ports included.
  - **S(c, d)**, the official CME daily settlement of contract c on trade date d.
    - Source: CME settlements, for example the Databento GLBX.MDP3 statistics schema (settlement
      statistic). It is paid and **not in D13's plan**. No free source with 2019-2026 history was found
      in E.0 [unverified] (section 7, item 2).
    - Availability: after d's settlement (grains 13:15 CT, livestock 13:00 CT, plus publication lag;
      E.2 records the timestamp). A rule reads S(c, d-1) and S(c, d-2) only on d.
  - **L(p, d)**, the daily price limit of product p in force on d, and whether it is the expanded limit.
    - Grain limits are "reset for the first trade date in May and the first trade date in November"
      (P-K6-048-b). Each is a 45-day average settlement times a product percentage, "Corn is
      multiplied by 7%" (P-K6-048-a).
    - "Expanded price limits are approximately 50 percent higher than daily price limits and remain
      in place until no futures contracts settle at limit". Expansion is linked across the soybean
      complex and across Chicago and KC wheat (P-K6-048-c).
    - "Spot month contracts are not subject to price limits. In Grain and Oilseed contracts, price
      limits are removed on the business day prior to first notice day" (P-K6-048-d).
    - Levels as of 2026-09-08: corn $0.30, SRW wheat $0.45, soybeans $0.85, meal $20.00, oil $0.045,
      lean hog $0.0425, live cattle $0.0850. Expanded levels: $0.45, $0.70, $1.30, $30.00, $0.070,
      $0.0625, $0.1275 (P-K6-047-a, P-K6-047-b).
    - **E.2 builds the historical limit table for 2019-2026** from CME's notices (dated, through
      Wayback), including the expanded state, the linkages and livestock limit changes. Limits
      change over time, so no 2026 level is used for an earlier date.
  - Limit prices: U(c, d) = S(c, d-1) + L(p, d) and D(c, d) = S(c, d-1) - L(p, d).
- **C11 Frequency (arithmetic from calendar counts, no price data).**
  - Research window 2025-04-01..2026-06-19: about 300 grain and livestock trade dates. It holds about
    14 WASDE releases (15 monthly dates from April 2025 to June 2026, with no October 2025 entry in
    ESMIS) and about 3 Grain Stocks dates that are not WASDE dates (end of June, September, March).
  - Confirmation window 2019-05-06..2024-02-29: about 1,200 trade dates and 58 WASDE releases (May
    2019 to February 2024).
  - **Consequence.** A WASDE-day member trades on about 5% of dates, with zeros on the rest (D5). It
    needs a net P&L of about 20 x eps_X per event to reach eps_X per trade date, so it is a likely
    "null at eps" or "inconclusive by design" case (D4; lead ruling 21:52, Q4: the power check
    decides).
- **C12 Release-minute cost.**
  - D8's five sample dates are 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11 and 2026-04-15. E.2
    checks whether any is an EC-USDA date. If none is, the grain 11:00 bucket is calibrated on
    non-release minutes.
  - Either way, D8's event-window rule charges every fill in [11:00, 11:30) on EC-USDA dates, and in
    [13:00, 13:30) on FOMC dates, the product's largest bucket. The same holds for the 07:30 Export
    Sales release, which no member trades.
  - Supporting evidence: the corn spread widens on report days, "USDA Grain Stock and Production-WASDE
    announcements significantly widen the BAS" (P-K6-021-b). Real-time releases bring "higher market
    liquidity costs" (P-K6-024-c).
- **C13 Price-limit proximity (D9.7) in K6.**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  - All seven products carry CME daily limits (P-K6-047-a). Topstep prohibits "Holding a position
    within 2% of a product's price lock limit" (F2.1). The harness encodes it: no entry, and an
    immediate exit, while the price is within 2% of U(c, d) or D(c, d).
  - This bites on report days. "prices reached a limit move only in about 2% of total observations"
    in crops, 4.4% in cattle and 8% in hogs, and "28.5% of the days with Hogs and Pigs report releases
    were subject to price limit moves" (P-K6-018-c, 1985-2018).
  - **Every member that holds across the 11:00 release** (CP2 and CP3 on grains, K6-crushgap-01,
    K6-wasdepre-01, K6-limitcont-01 on grain release days, K6-ml-01):
    - it is never in a position when the market is already locked or within the band before the
      release, because the entry guard blocks entry and the immediate exit closes a position when
      the price enters the band;
    - if the release itself carries the price into the band, the D9.7 exit fills at the first bar
      D9.5a allows, 11:02 at the earliest;
    - so the position can sit inside the band for up to about two minutes. This residual is common to
      the ports and is put to the lead (section 7, item 3). The arithmetic of "within 2%" is item 4.

---

## 1. Members

### K6-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording. R-03: on HE and LE, which have no overnight session, the trade date's first bar is the 08:30 open, so the signal is the first 30 minutes of the day session (the (b) form); D6 now says so; the two trials are kept.]
- **Cluster:** K6. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures** (each a separate trial): ZC, ZW, ZS, ZM, ZL, HE, LE. Each is traded only if D2
  admits the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log
  A10 and A28), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the
    trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in
    the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after
    C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else no
    trade."
  - **K6 log.** No passed K6 item tests this family on a K6 product. Rosa's intraday momentum names no
    K6 product (R-K6-006), and the coffee intraday momentum paper is not a K6 product (R-K6-032). The
    port is not a duplicate of any cluster member.
- **Instantiated.**
  - **Grains (O 08:30, C 13:15, F 13:18).**
    - Signal: close of the bar at 08:59 minus the open of the trade date's first bar, the first bar
      at or after the 19:00 CT evening open before d (C3).
    - Entry: market intent on the bar at 12:44, filling at the 12:45 open.
    - Exit: market intent on the first bar at or after 13:13, filling nominally at the 13:14 open.
    - Hold 29 minutes; window 12:45-13:14.
  - **Livestock (O 08:30, C 13:00, F 13:03).**
    - Signal: the trade date's first bar is the 08:30 bar (C3), so the signal is the first half hour
      only: close of the 08:59 bar minus open of the 08:30 bar. The (a) form's overnight component
      does not exist for livestock (section 7, item 6).
    - Entry: market intent on the bar at 12:29, filling at 12:30.
    - Exit: market intent on the first bar at or after 12:58, filling at 12:59. Hold 29 minutes.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid, with history
  2019-05..2026-06. The latest signal input, the 08:59 bar, is available at 09:00 CT.
- **Order type:** market. **Sizing:** q = 1 (C6).
- **Parameters:** O+29, C-31 and C-2 from D6. **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date, held 29 minutes. Floor (at most 20 entries
  a day, 2-minute minimum hold, 10-minute mean hold): ok.
- **Falsification:** the standard condition only (a port). UCB95 of the member's mean net daily P&L
  per contract below eps_X, at >= 80% achieved null power on the confirmation window, counts against
  it.
- **Topstep check:**
  1. Flat by F: last fill 13:14 (grains) or 12:59 (livestock).
  2. Order type: market.
  3. D9.4: one trade a day, no stops or brackets.
  4. Star: no K6 product is starred.
  5. News: on FOMC days the grain position spans the 13:00 statement ("All products", F6) at 1 lot,
     which F6.3 allows, and the 13:14 exit pays D8's event-window cost (C12). Livestock exits at
     12:59, before the statement.
  6. D9.5a: no fill falls in [13:00, 13:02) or [11:00, 11:02).
  7. Position limit: 1 lot-equivalent.
  8. D9.7: the harness guard applies (C13). The grain window 12:45-13:14 does not contain 11:00.
- **Data needed:** ohlcv-1m of each admitted K6 vehicle, research window 2025-04-01..2026-06-19 and
  confirmation window S_X..2024-02-29 (D4). External: EC-CAL, EC-LIM (for D9.7).
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-cp2-01 (core port CP2, opening-range breakout)
- **Cluster:** K6. **Products read:** own vehicle.
- **Traded exposures:** ZC, ZW, ZS, ZM, ZL, HE, LE, one trial each. Each is traded only if D2 admits
  it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Port of MES B-H1 hold 75 (class C2), as fixed in D6 row CP2 with the 21:12 and 21:52
  amendments.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market
    intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes
    after the fill, or the engine's forced flatten at F if earlier."
  - "4 ticks of P" means 4 minimum increments of the exposure's most active contract (D6, ruling
    21:52). Each K6 exposure has one contract, so there is no ambiguity.
  - **K6 log:** no opening-range-breakout source on a K6 product was logged.
- **Instantiated.**
  - Opening range: the bars opening in [08:30, 08:45).
  - Eligible bars: those opening in [08:45, 13:15) for grains and [08:45, 13:00) for livestock.
  - Buffer: the table in C7 (ZC, ZW, ZS 0.01 USD/bu; ZM 0.40 USD/short ton; ZL 0.0004 USD/lb; HE and
    LE 0.001 USD/lb).
  - Entry: the first eligible bar whose close is >= OR_high + buffer buys, and one whose close is
    <= OR_low - buffer sells. One entry per trade date.
  - Exit: 75 minutes after the fill (the exit intent on the 75th bar after the entry-intent bar,
    filling at the next open), or F. For grains an entry filled after 12:03 is closed at F = 13:18;
    for livestock, after 11:48 at F = 13:03.
  - Holding horizon: up to 75 minutes. Session window 08:46-13:18 (grains) or 08:46-13:03
    (livestock).
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known
  at 08:45 CT.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** OR 15 minutes, buffer 4 ticks, hold 75 minutes (D6, a literal port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held up to 75 minutes. Floor: see Topstep item 3.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F.
  2. Order type: market.
  3. D9.4: one trade a day, no stops. **Edge case for the lead** (section 7, item 5). On FOMC days a
     livestock entry intent on the 12:59 bar would fill at 13:00, which D9.5a defers to 13:02. That
     leaves one bar to F = 13:03, breaking D9.3(b)'s 2-minute minimum. The grain latest fill (13:15)
     still leaves three bars to F.
  4. Star: none.
  5. News: a grain position may span the 11:00 Crop Production release ("Crop Production | 11:00 AM
     | ZC, ZS, ZW, ZM, ZL", F6) at 1 lot, which F6.3 allows.
  6. D9.5a: a fill that would land in [11:00, 11:02) or [13:00, 13:02) is deferred to +2 min.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: C13, including the release residual.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows;
  EC-CAL, EC-USDA, EC-FOMC (harness), EC-LIM.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-cp3-01 (core port CP3, prior-close location)
- **Cluster:** K6. **Products read:** own vehicle.
- **Traded exposures:** ZC, ZW, ZS, ZM, ZL, HE, LE. Each is traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6), as
  fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L
    over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family
    H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market
    intent on the O bar of day d. Exit: first bar at or after C-2 min."
  - **K6 log.** A close at the daily limit has CLV = 1 (limit up) or 0 (limit down). Every
    K6-limitcont-01 trade is therefore a same-direction subset of CP3's trades, entered 14 minutes
    later. That is a correlated member, not a duplicate (see K6-limitcont-01 and section 7, item 8).
- **Instantiated.**
  - **Grains.** The daily bar is [08:30, 13:15): O_d is the 08:30 open, and C_d the close of the 13:14
    bar. The complete-day test requires the 08:30 and 13:14 bars, a date with no early halt, and one
    instrument_id over [08:30, 13:15). Entry: market intent on the 08:30 bar of d, filling at the
    08:31 open. Exit: first bar at or after 13:13, filling at 13:14. Hold about 283 minutes.
  - **Livestock.** The daily bar is [08:30, 13:00), with C_d the close of the 12:59 bar. Entry fills
    at 08:31. Exit: first bar at or after 12:58, filling at 12:59. Hold about 268 minutes.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of d's 08:30 bar.
  - **CLV cuts:** non-strict 0.8 and 0.2 (H6).
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar
  is complete at 13:15 CT (grains) or 13:00 CT (livestock) on d-1.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 4.5 hours. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:14 or 12:59.
  2. Order type: market.
  3. D9.4: the grain entry fills one minute after the 08:30 reopen that follows the pause. It is a
     market order in a two-sided reopened market, not a stray-fill strategy (section 7, item 12).
  4. Star: none.
  5. News: grains hold through the 11:00 release on EC-USDA days, and every product holds through
     13:00 on FOMC days, at 1 lot (F6.3).
  6. D9.5a: no fill in a guard window.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: C13. The day after a limit close is where CP3 is most exposed to the band, since it buys
     after limit-up closes.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows;
  EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-crushgap-01 (soybean crush: the overnight gap in the processing margin reverses in the day session; single-leg)

> [Lead ruling, 01:52 PDT 2026-09-24, on this writer's question 1: traded on ZS ONLY (1 trial); ZM and ZL removed. The evidence is about the crush spread, and a spread cannot meet the 1-lot cap; the most liquid leg is kept. Where this entry says ZM or ZL are traded, read ZS only.]
- **Cluster:** K6. **Products read:** ZS, ZM and ZL bars (all three are needed for the margin); EC-CAL.
- **Traded exposures** (each a separate trial, one leg per trial): ZS, ZM, ZL. Each is traded only if
  D2 admits it. The other two legs are read even if not admitted (C8). **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism.**
  - **What is claimed** (K6-001, full text; pit era 1978-1991).
    - The gross processing margin (GPM = meal and oil value minus beans) reverses at the open. "If
      the GPM on the open is less (greater) than the previous day's close, a reverse crush (normal
      crush) spread is placed. In all cases, the position is liquidated on the close of the same day"
      (P-K6-001-a).
    - The GPM's open-to-close change and its close-to-open gap correlate at -0.49 (1978-1987) and
      -0.43 (1987-1991) (P-K6-001-d).
    - "the GPM at the opening tends to be lower than the previous close and then 'trade up' during the
      day" (P-K6-001-e).
    - Net of 1.5 cents per bushel round-trip costs (P-K6-001-b), the mean profit per trade at filters
      of 0 / 1 / 2 / 3 cents is "-0.36 0.35 1.02 1.74", over "3352 1861 922 457" trades (P-K6-001-f).
  - **Why it should survive the modern session** (reasoned from K6-026). In 2015 one-minute data, "A
    high level of cointegration is indeed observed during session 2 trading hours, which fades away
    during session 1" (P-K6-026-c). Session 2 is 8.30 AM to 1.20 PM and session 1 the 7 PM to 7.45 AM
    electronic session (P-K6-026-b). A margin that drifts from equilibrium overnight and is pulled back
    in the day session is the pattern K6-001 trades.
  - **Direction.** From P-K6-001-d and P-K6-001-e: after a GPM gap down, the day-session GPM change is
    expected positive. The position that gains is long GPM, that is long meal, long oil and short
    beans. This agrees with the source's "reverse crush" after a gap down.
  - **The single-leg step** (an inference, untested by any source).
    - A spread position is not allowed (D9.5; section 2, X-01 and X-02), so each leg is traded alone,
      in its GPM-reversal direction.
    - The claim tested is that a leg carries part of the documented spread reversal. The leg's own
      directional move, which the GPM gap does not predict, is noise in this test.
    - The source does not say which leg adjusts, so all three are tested (3 trials). Section 7, item 1
      gives the lead the 1-trial alternative.
  - **Evidence limits and against.**
    - Pit-era prints ("small unrepresentative trades occurring at the open", log quality tells).
    - Floor-trader costs, strongly year-dependent profits, and filters with no out-of-sample split
      (log quality tells).
    - K6-026 finds that "Hardly any cointegration was detected using Johansen's approach"
      (P-K6-026-e), and has one year of data (P-K6-026-d).
    - Simon's reversion to "its most recent 5-day average" (P-K6-008-a) and Mitchell's "Winning trades
      are significantly shorter" (P-K6-044-a) are abstracts only and support reversion in general.
  - **Classification:** new to the program (an inside-K6 spread signal; the log tags the
    opening-reversal element as a spread version of D.1 family C).
- **Margin definition.**
  - GPM = 0.022 x P_ZM + 11 x P_ZL - P_ZS, in USD per bushel, with P_ZM in USD per short ton, P_ZL in
    USD per pound and P_ZS in USD per bushel.
  - Each is converted from GLBX.MDP3's raw units by the contract specification (C7). E.2 confirms the
    units.
  - The weights come from CME: "11 pounds of soybean oil, 44 pounds of 48 percent protein soybean
    meal" per 60-lb bushel (P-K6-050-a), and 44/2000 = 0.022.
  - CME's quoted formula, "[(Price of Soybean Meal ($/short ton) x .022) + Price of Soybean Oil (¢/lb)
    x 11] – Price of Soybeans ($/bu.)" (P-K6-050-b), puts the oil term in cents. The unit-consistent
    form above uses USD per pound.
  - K6-001 used 48 lb of meal. The current 44 lb is used here (log note to K6-050).
  - **Contract months.** Each leg uses its own vehicle's contract under E.2's roll convention, so the
    months may differ (for example November soybeans against December meal and oil). The signal is
    the change of the GPM from one close to the next open, in which a fixed inter-month difference
    cancels, so the mismatch is accepted (section 7, item 10).
- **Signal.** G(d) = GPM_open(d) - GPM_close(d-1).
  - GPM_close(d-1) uses the closes of the three 13:14 bars of the previous grain trade date d-1 in
    EC-CAL.
  - GPM_open(d) uses the opens of the three 08:30 bars of d.
  - For each leg, its 13:14 bar on d-1 and its 08:30 bar on d must exist and carry the same
    instrument_id. Otherwise there is no trade on d.
- **Entry rule.**
  - If G(d) <= -0.02: on the traded leg, BUY ZM, BUY ZL, or SELL ZS.
  - If G(d) >= +0.02: SELL ZM, SELL ZL, or BUY ZS.
  - Otherwise no trade.
  - Market intent on the 08:30 bar of d, filling at the 08:31 open.
- **Exit rule:** market intent on the first bar at or after 13:13, filling at the 13:14 open.
- **Holding horizon:** about 283 minutes. **Session window:** 08:31-13:14 CT. Flat by F.
- **Data fields read:**
  - ZS, ZM and ZL ohlcv-1m open, close and instrument_id (C8). Paid, with 2019-05..2026-06 history.
    The d-1 inputs are available at 13:15 CT on d-1, and the 08:30 bars at 08:31 CT on d.
  - EC-CAL, known in advance.
- **Order type:** market. **Sizing:** q = 1 of the traded leg.
- **Parameters.**
  - Weights 0.022 and 11 (P-K6-050-a, P-K6-050-b).
  - **Filter 0.02 USD/bu (2 cents per bushel).** P-K6-001-f: the 1, 2 and 3 cent filters are all
    positive net. The middle value is a judgment. The 3-cent filter's larger mean is deliberately not
    chosen, to avoid taking the best in-sample value.
  - Anchor at the previous close, entry at the open, exit at the close (P-K6-001-a). The pit open and
    close map to the 08:30 day open and the C-1 (13:14) bar, as in CP3 (judgment).
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date per leg, held about 4.7 hours.
  - Frequency is unknown for 2019-2026. In the source, the 2-cent filter traded 922 of 3,352 days
    (P-K6-001-f), about 28%. Today's overnight session and price levels may change that; E.2
    measures it on the research window.
  - Floor ok.
- **Falsification.**
  - The standard condition, per traded leg.
  - **Sign check (reported beside the verdict, not a separate test):** the mean over trades of
    w_leg x (-sign(G)) x (open of the 13:14 bar - open of the 08:31 bar), in the leg's ticks, is
    positive, where w_leg = +1 for ZM and ZL and -1 for ZS.
  - **Diagnostic (reported):** on eligible days, corr(G(d), GPM at the 13:14 open minus GPM at the
    08:31 open). The mechanism predicts it is negative (the source's -0.49 and -0.43, P-K6-001-d). A
    negative spread correlation with a failing leg would locate the failure in the single-leg step,
    not in the mechanism.
- **Topstep check:**
  1. Flat by F: last fill 13:14.
  2. Order type: market.
  3. D9.4: one trade a day, no stops. The entry is one minute after the 08:30 reopen, as in CP3
     (section 7, item 12).
  4. Star: none.
  5. News: holds through the 11:00 Crop Production release on EC-USDA days at 1 lot. ZS, ZM and ZL
     are all on Topstep's Crop Production row. F6.3 allows it.
  6. D9.5a: no fill in a guard window.
  7. Position limit: 1 contract, never two legs.
  8. D9.7: the entry guard applies to the traded leg at 08:31. Expanded limits are linked across the
     soybean complex (P-K6-048-c), so E.2's table must carry the linkage. The release residual is in
     C13.
- **Data needed:** ohlcv-1m of ZS, ZM and ZL (all three, whichever is traded) over the research and
  confirmation windows; EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted leg among ZS, ZM and ZL (at most 3).

### K6-limitcont-01 (day after a limit close: day-session continuation in the limit direction)

> [Lead ruling, 01:52 PDT, question 6: traded on HE and LE ONLY (2 trials); the five grain exposures removed. Its trades are largely a subset of CP3's, so the grain trials add little information. Where this entry lists grain exposures, read HE and LE only.]
- **Cluster:** K6. **Products read:** the traded vehicle; EC-LIM (settlements and limit table);
  EC-CAL.
- **Traded exposures** (each a separate trial): ZC, ZW, ZS, ZM, ZL, HE, LE. The source's nine
  commodities include "soybean oil (BO), corn (C), ... live cattle (LC), lean hogs (LH), soybean (S),
  soybean meal (SM), and soft red winter wheat (W)" (P-K6-002-e). Each is traded only if D2 admits
  it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed.**
    - "Consistent with delayed price discovery, returns continue in the same direction after limit
      days and do not reverse after one week, whereas returns are small after large price moves that
      do not hit limits" (P-K6-002-a).
    - "For limit up days, the average return on the following day is 40 to 62 basis points, and for
      limit down days, the average return on the following day is -38 to -63 basis points"
      (P-K6-002-b; P-K6-002-c). These are close-to-close, 1991-2016 (P-K6-002-e), over 2,063 limit ups
      and 2,393 limit downs (P-K6-002-f).
    - Park (abstract only, contracts unnamed): "prices continue to rise on average the day after an
      up-limit day" (P-K6-003-a).
  - **What the program can hold, and the evidence against.**
    - The next day's open-to-close part, which is all a day-session rule can hold, is not reported
      [unverified].
    - The one split the source gives points the other way. "a 1% increase in the return calculated
      from limit day close to options-implied prices is associated with a 0.76% increase in the
      close-to-open futures returns, and 0.15% increase in the close-to-close futures returns"
      (P-K6-002-d). If both coefficients come from the same events (not stated), then on that
      regressor the open-to-close part is 0.15 - 0.76 = -0.61. The day session would then partly
      reverse what the open priced.
    - After a lock in LE and HE, price limits "add to the high uncertainty that precedes the limit
      move, leading to significantly higher volatility and lower liquidity when trading resumes"
      (P-K6-035-a, abstract).
    - Limit sizes have changed since the sample: they are now reset semi-annually (P-K6-048-a,
      P-K6-048-b). The 1991-2016 frequency does not carry over.
  - **Classification:** new to the program (limit state).
  - **Relation to CP3:** every trade is a same-direction subset of K6-cp3-01's trades (C13; section
    7, item 8). The distinguishing claim is the limit itself: P-K6-002-a contrasts limit days with
    large moves that do not hit the limit.
- **Event.** Trade date d whose previous trade date d-1 closed at the limit for contract c, the
  contract of d's 08:30 bar:
  - limit-up close: S(c, d-1) = S(c, d-2) + L(p, d-1);
  - limit-down close: S(c, d-1) = S(c, d-2) - L(p, d-1);
  - where L is the limit in force on d-1 (expanded where in force), from EC-LIM (C10).
  - A contract without a limit on d-1 (P-K6-048-d) does not qualify.
- **Entry rule:** market intent on the bar at 08:44, filling at the 08:45 open. BUY after a limit-up
  close; SELL after a limit-down close. The D9.7 entry guard applies.
- **Exit rule:** market intent on the first bar at or after C-2 (grains 13:13, filling at 13:14;
  livestock 12:58, filling at 12:59), or earlier by D9.7's immediate exit.
- **Holding horizon:** about 269 minutes (grains) or 254 minutes (livestock). **Session window:**
  08:45-13:14 or 08:45-12:59. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open and instrument_id (C8). Paid, 2019-05..2026-06. The 08:44 bar is available
    at 08:45 CT.
  - S(c, d-1) and S(c, d-2): official settlements (C10). Paid, not yet in D13. Available after d-1's
    settlement, before d's 08:30 open.
  - L(p, d-1) and the expanded state: the CME limit table E.2 builds (C10; free CME notices, dated).
    Known before d-1.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - **Entry at 08:45 (O + 15), a judgment.** It avoids the first 15 minutes after the day open, where
    the lock-release illiquidity (P-K6-035-a) and the open's concentration of quotes (P-K6-023-c,
    LE) fall. It also stays clear of the D9.4 "gapped markets" clause. The source measures
    close-to-close, which gives no intraday entry time.
  - **Exit at C-2:** the port convention. The source's horizon is the next day's close (P-K6-002-b).
  - **Limit close:** exact equality of the settlement with the limit price (judgment: the source's
    limit days are closes at the limit, per the log's mechanism line). E.2 applies CME's settlement
    rounding.
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per qualifying day.
  - The 2019-2026 frequency is unknown (variable limits since the source's sample).
  - Upper-bound guide: a limit move on about 2% of crop days, 4.4% of cattle days and 8% of hog days
    (P-K6-018-c, 1985-2018, "reached a limit move", which may count intraday touches). That is at most
    about 6, 13 and 24 events per product in the research window, and about 24, 53 and 96 in the
    confirmation window.
  - Grains will likely be "inconclusive by design" at D4's power check (section 7, item 7).
  - Floor ok.
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of direction x (open at the exit fill - open at the entry
    fill), in ticks, is positive over qualifying days. It is reported with the event count per
    exposure.
  - **Also reported:** the mean close-to-open part, S(c, d-1) to d's 08:30 open, in the same
    direction. The source's continuation may lie there, outside the member's hold.
- **Topstep check:**
  1. Flat by F.
  2. Order type: market.
  3. D9.4: one entry, 15 minutes after the day open. It never trades on the lock day itself or at a
     lock's reopening (X-12).
  4. Star: none.
  5. News: on grain EC-USDA days the hold spans 11:00 at 1 lot (F6.3).
  6. D9.5a: fills at 08:45, 13:14 and 12:59 are outside the guard windows.
  7. Position limit: 1 lot-equivalent.
  8. **D9.7.** The day after a limit close is exactly when the price may sit near the (expanded)
     limit. The entry guard blocks an 08:45 entry within 2% of U(c, d) or D(c, d), and the immediate
     exit applies afterwards. E.2 builds the historical limit table with the expanded state and its
     linkages (P-K6-048-c). The release residual on grain EC-USDA days is in C13.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows.
  External: settlements (C10), the CME limit table, EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-wasdepre-01 (WASDE day: the day-session drift before the 11:00 CT release continues through it)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP: K6-027's sample window is not recorded (a 2026 paper); treated as overlapping until E.1 records it. R-10: the D9.7 "release residual" text in this entry is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard.]
- **Cluster:** K6. **Products read:** the traded vehicle; EC-WASDE; EC-CAL.
- **Traded exposures** (each a trial): ZC and ZS, the products of the source ("U.S. corn and soybean
  ending stock data and relevant corn and soybean futures", P-K6-027-a). Each is traded only if D2
  admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed.**
    - "directionally correct drift prior to release suggests that we also observed informed trading
      and/or superior internal research" (P-K6-027-a, WASDE, abstract only; its window and magnitudes
      are [unverified]).
    - "we provide evidence that informed trading exists in commodity markets before the release date"
      (P-K6-043-a, WASDE, abstract only; the horizon is likely daily).
    - "Other more subtle reactions occur in the last trading session before USDA announcements as
      traders adjust their market exposure in anticipation of the release" (P-K6-015-b, corn,
      2009-2012).
  - **The rule-3 route.** The surprise itself needs proprietary polls (P-K6-049-e), so it is observed
    through price. The reasoning:
    1. If informed trading moves the price toward the not-yet-public number before the release, the
       sign of the day-session move before the release carries the sign of the coming surprise.
    2. The release response has the surprise's sign: "a 1% larger-than-expected USDA production
       surprise is followed by a reduction in futures price of about 1.1%" (P-K6-011-a).
    3. So a position in the direction of the pre-release drift, held across the release, collects the
       rest of the drift and the release response.
  - **Evidence limits.**
    - K6-027 and K6-043 are abstracts. K6-027's venue and peer-review status are [unverified], and its
      sample may overlap the confirmation window [unverified] (section 7, item 11).
    - The logged efficiency results, "little evidence exists to support systematic under‐ or
      overreactions" (P-K6-015-b) and "Return correlations provide little evidence to support
      systematic under- or overreaction" (P-K6-014-b), concern returns after the release. They do not
      test the pre-release drift, so they neither support nor contradict it.
  - **Classification:** port of D.1 family E (pre-release window), grain-specific. D6 does not port
    family E, so this is a cluster member.
- **Event set:** EC-WASDE dates (C9a), T = 11:00 CT. WASDE and Crop Production share every date.
- **Signal:** Dr = close of the vehicle's bar at 10:29 minus the open of its bar at 08:30, in ticks.
  Both bars must exist with one instrument_id. Dr = 0 means no trade.
- **Entry rule:** market intent on the bar at 10:29, filling at the 10:30 open, in the direction of
  sign(Dr).
- **Exit rule:** market intent on the bar at 11:14, filling at the 11:15 open.
- **Holding horizon:** 45 minutes. **Session window:** 10:30-11:15 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open, close and instrument_id (C8). Paid. The inputs are available at 08:31 and
    10:30 CT.
  - EC-WASDE date. Free; the USDA schedule and ESMIS record have 2019-2026 history (C9a). Known before
    d.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - **Drift window 08:30-10:29, a judgment.** It is the day session, which "contains the most trading
    activity" (P-K6-026-b), up to 30 minutes before the release. The source's drift window is
    [unverified].
  - **Entry 30 minutes before the release, a judgment.** It precedes the pre-release volatility rise
    "between 20 and 10 minutes before the report release" (P-K6-029-a), so the entry fill is not in
    that window.
  - **Exit at T + 15.** Reactions "persist for approximately ten minutes" (P-K6-015-b). In-session
    releases produce a spike "for five to six minutes" (P-K6-014-a). T + 15 is after both and clear of
    D9.5a.
  - **Sign only, with no threshold** (judgment, as CP1).
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per WASDE date: about 14 research and 58 confirmation
  events (C11), about 5% of trade dates. Held 45 minutes. Floor ok.
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(Dr) x (open of the 11:15 bar - open of the 10:30 bar),
    in ticks, is positive.
  - **Reported split:** the pre-release part (10:30 to the 11:00 open) and the release part (the 11:00
    open to 11:15).
- **Topstep check:**
  1. Flat by F: last fill 11:15.
  2. Order type: market.
  3. D9.4: entry 30 minutes before and exit 15 minutes after the release. No fill in a release minute,
     no gapped-market entry.
  4. Star: none.
  5. News: holds through the Crop Production and WASDE release at 1 lot ("Crop Production | 11:00 AM
     | ZC, ZS, ZW, ZM, ZL", F6). F6.3 prohibits only full maximum size.
  6. D9.5a: no fill in [11:00, 11:02) by construction. The 11:15 exit pays D8's event-window cost
     (C12).
  7. Position limit: 1 lot-equivalent.
  8. **D9.7.** The 10:30 entry is blocked when the price is within 2% of U or D, so the member is never
     in when the market is near its limit before the release. If the release carries the price into
     the band (report-day locks: P-K6-011-e; P-K6-018-c), the immediate exit fills at 11:02 at the
     earliest (C13; section 7, item 3).
- **Data needed:** ohlcv-1m of ZC and ZS over the research and confirmation windows; EC-WASDE,
  EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted exposure among ZC and ZS (at most 2).

### K6-wasdepost-01 (WASDE day: corn continues its release response to the close)
- **Cluster:** K6. **Products read:** ZC; EC-WASDE; EC-CAL.
- **Traded exposure:** ZC only, the source's product (K6-037 is corn). Traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed.**
    - "the USDA's influence on corn prices remains embodied in corn futures for several days after
      the release of USDA's WASDE report" (P-K6-037-a). Lag dummies for days 2-4 are used
      (P-K6-037-c). This is daily OHLC, 1999-2017 (P-K6-037-d), and the open-to-close part is not
      separated.
    - "unconditional elasticities that are persistently below unity, consistent with incomplete
      post-report alignment of trader expectations" (P-K6-028-b, abstract, corn, 2013-2020).
    - Reasoning: if the adjustment to the WASDE news is incomplete at the end of the release window,
      the rest of the day session continues the release response.
  - **Evidence against (the balance of the log predicts a null).**
    - "on average, corn market prices respond to USDA news and those prices tend to remain at about
      the level of the initial response over the next two trading weeks" (P-K6-011-d, August reports
      2009-2019, figure-based).
    - "little evidence exists to support systematic under‐ or overreactions in prices" (P-K6-015-b).
    - "Return correlations provide little evidence to support systematic under- or overreaction"
      (P-K6-014-b, soybeans).
    - The member tests the null at the funnel's bar.
  - **Classification:** port of D.1 family E (the E-H2 post-release momentum form), corn-specific,
    as a cluster member.
- **Event set:** EC-WASDE dates, T = 11:00 CT.
- **Signal:** R = close of the ZC bar at 11:14 minus close of the ZC bar at 10:59, in ticks. Both bars
  must exist with one instrument_id. R = 0 means no trade.
- **Entry rule:** market intent on the bar at 11:14, filling at the 11:15 open, in the direction of
  sign(R).
- **Exit rule:** market intent on the first bar at or after 13:13, filling at the 13:14 open.
- **Holding horizon:** about 119 minutes. **Session window:** 11:15-13:14 CT. Flat by F.
- **Data fields read:** ZC ohlcv-1m close, open and instrument_id (C8). Paid. The signal is available
  at 11:15 CT. EC-WASDE is free and known before d.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - **Response window from the T - 1 to the T + 14 bar close, a judgment.** It covers the spike
    (P-K6-014-a) and the ten-minute reaction (P-K6-015-b), and ends where K6-wasdepre-01 exits.
  - **Exit at C-2:** the port convention. The source's horizon is several days, and the day-session
    remainder is what the program can hold.
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per WASDE date: about 14 research and 58 confirmation
  events. Held about 2 hours. Floor ok.
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(R) x (open of the 13:14 bar - open of the 11:15 bar),
    in ticks, is positive.
- **Topstep check:**
  1. Flat by F: 13:14.
  2. Order type: market.
  3. D9.4: entry 15 minutes after the release, after the spike, not in a gapped market.
  4. Star: none.
  5. News: 1 lot. The position spans 13:00 on the rare dates that are both WASDE and FOMC dates (E.2
     counts them).
  6. D9.5a: the 11:15 entry is outside [11:00, 11:02) but inside D8's 30-minute event window, so it
     pays the largest bucket.
  7. Position limit: 1 lot-equivalent.
  8. **D9.7.** The entry guard blocks the 11:15 entry when the release has moved the price within 2%
     of the limit, the kind of day in P-K6-011-e ("the market locked limit down"). The member never
     enters a near-limit market. The largest-response days are therefore excluded by construction,
     and the reported sign check states how many were.
- **Data needed:** ohlcv-1m of ZC over the research and confirmation windows; EC-WASDE, EC-CAL, EC-LIM.
- **Trials in N:** 1.

### K6-ovr-01 (hourly overreaction reversal in grains)

> [EXCLUDED by the lead, 01:52 PDT, question 6: no grain-specific result is logged and one logged source argues against it (K6-025). Moved to the excluded list; 0 trials. The entry is kept below for the record only.]
- **Cluster:** K6. **Products read:** the traded vehicle; EC-USDA; EC-CAL.
- **Traded exposures** (each a trial): ZW, ZC, ZS, ZL, the K6 products in the source's sample:
  "wheat (W), corn (C), soybeans (S), soybean oil (BO)" (P-K5-029-b [K6]). Soybean meal and livestock
  are not in the sample and are not traded. Each is traded only if D2 admits it. **Vehicle:** D2
  (chosen in E.2).
- **Mechanism.**
  - **What is claimed.** K5-029 is a panel source; its [K6] passages are in the K5 log.
    - It examines "the overreaction behavior of 20 commodity futures based on intraday data"
      (P-K5-029-a [K6]).
    - Method: large intraday price changes beyond a decile threshold, at 1-minute to 1-hour
      frequencies, are followed by reversals (K5 log mechanism line). The decile and 1-hour wording
      is in P-K5-029-c ("first decile overreactions for the 1-h frequency"), which is tagged [K5] and
      [K4]. It is used here for the method only, not as a grain result.
    - Costs: "As transaction costs in futures trading are negligible, the net-of-fees trading results
      would be still positive in both periods" (P-K5-029-d [K6]).
  - **Evidence limits.**
    - No grain-specific result is in the verified passages. The abstract ranks "soft and metal
      commodities" below "precious metals and especially energy commodities" and does not rank
      grains (P-K5-029-a).
    - The data are six months, Covid-dominated (2019-11-20..2020-06-03), inside the confirmation
      window.
    - The holding period is [unverified]. Costs are asserted, not modelled.
  - **Evidence against, for ZC.**
    - Flash events in corn and lean hogs "are heavily influenced by unanticipated changes in
      fundamentals that may lead to a new equilibrium price" (P-K6-025-a, abstract).
    - About two thirds of corn 5-minute jump clusters have no same-day news (P-K6-033-a). There is no
      reversal test either way.
  - **Classification:** port of D.1 family C (magnitude-conditioned reversal), tested
    product-specifically. D6 does not port family C, so this is a cluster member.
- **Decision times:** t in {09:30, 10:30, 11:30, 12:30} CT. These are the four whole hours after
  O = 08:30 whose 40-minute hold ends before C-2.
  - On EC-USDA dates the 10:30 and 11:30 decisions are skipped: their holding or signal interval
    contains the 11:00 release and D8's event window.
  - Reason (judgment): the logged report responses are efficient (P-K6-014-b, P-K6-015-b), which is
    a different mechanism from overreaction.
- **Signal:** r(t) = (close of the bar at t - 1 - open of the bar at t - 60) / open of the bar at
  t - 60. Both bars must exist with one instrument_id, and the denominator must be > 0.
- **Reference set and cuts.**
  - The reference set is r(tau) at the same four clock times on the 20 most recent earlier eligible
    trade dates (full sessions in EC-CAL, not roll-blackout), excluding skipped (tau, date) pairs.
  - At least 60 values are required, else no trade at t.
  - P10 and P90 = np.percentile(values, [10, 90], method="linear").
  - Warm-up: the first 20 eligible dates of each window. Holdout-2 is sealed, so no earlier bars are
    used.
- **Entry rule:** r(t) <= P10 means BUY; r(t) >= P90 means SELL; otherwise no trade. Market intent on
  the bar at t - 1, filling at the open of the bar at t.
- **Exit rule:** market intent on the bar at t + 39, filling at the open of t + 40. At most one
  position is open; the next entry fills at t + 60.
- **Holding horizon:** 40 minutes. **Session windows:** 09:30-10:10, 10:30-11:10, 11:30-12:10 and
  12:30-13:10 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8), all closed at or before
  t; EC-USDA; EC-CAL. All free except the bars.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - 60-minute signal: the source's 1-hour frequency.
  - P10 and P90: the source's decile (P-K5-029-c, method).
  - **20-date reference, a judgment:** the program's trailing-state length (D15.4 B4). The source's
    threshold construction is not in the logged passages.
  - **40-minute hold, a judgment:** the longest uniform hold at which the 12:30 position is flat by
    13:10, before C-2 and F. The source's holding period is [unverified].
  - The EC-USDA skip rule (above).
  - **Grid:** none.
- **Expected entries and hold:** if the trailing distribution is stable, about 20% of eligible
  decisions qualify, about 0.8 entries per day per exposure (at most 4; at most 2 on EC-USDA dates).
  Held 40 minutes. Floor ok.
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of -sign(r(t)) x (open at t + 40 - open at t), in ticks, is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 13:10.
  2. Order type: market.
  3. D9.4: at most 4 entries a day, 40-minute holds, no stops. Not scalping.
  4. Star: none.
  5. News: the 12:30 position spans the 13:00 FOMC statement on FOMC days at 1 lot. No position spans
     11:00 on EC-USDA dates.
  6. D9.5a: fills fall at :30 and :10, never in [11:00, 11:02) or [13:00, 13:02). The 13:10 exit on
     FOMC days pays D8's event-window cost.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: a large hourly move can end near the limit. The entry guard blocks entry within 2% (C13).
- **Data needed:** ohlcv-1m of the ZW, ZC, ZS and ZL vehicles over the research and confirmation
  windows; EC-USDA, EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted exposure among ZW, ZC, ZS and ZL (at most 4).

### K6-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 ADV order): ZC, ZS, ZL, ZM, ZW, LE, HE; if none is admitted, no ML member. Features unchanged. R-11 (NOTE): the first decision time that cannot trade is dropped from the decision grid by D15.3's row rule.]
- **Traded vehicle: corn, ZC** (D2 chosen in E.2; ZC is the exposure's only contract).
  - **Reason:** corn is the K6 product the log documents most at intraday and release horizons:
    K6-006, 010, 011, 015, 016, 017, 018, 021, 024, 025, 027, 028, 029, 030, 031, 033, 034, 037 and
    045, against about twelve soybean items and six livestock items. It also has the cluster's highest
    public ADV (505,663, 2026 Jan-Aug; D1 table).
  - **No fallback is declared.** The features are corn-specific (the ZC limit state and corn Crop
    Progress). If D2 does not admit ZC, the lead decides.
- **Products the features read:**
  - ZC, and ZS bars. ZS is needed as a leg even if soybeans are not admitted; E.2 then buys its
    history (C8).
  - Calendars: EC-USDA, EC-CAL.
  - EC-LIM (settlements and limit table, C10) and EC-CP (NASS Crop Progress, C9d).
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12. Throughout, t_j is the decision
  time, "the bar at t_j - 1" is the last bar closed at t_j, and tick is ZC's 0.0025 USD/bu unless
  stated.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | usda_phase | If d is an EC-USDA date: -1 if t_j < 11:00, +1 if t_j >= 11:00. If d is not: 0 | K6-038 P-K6-038-a, P-K6-038-b; K6-040 P-K6-040-a, P-K6-040-b; K6-049 P-K6-049-a, P-K6-049-c (schedule, 11:00 CT); K6-029 P-K6-029-a (effects begin before the release and "last till the end of the trading session"); K6-027 P-K6-027-a (pre-release drift) | schedule known before d (C9a); depends on the clock only |
| KF2 | usda_resp | If d is an EC-USDA date and t_j >= 11:14: (close of the ZC bar at 11:13 - close of the ZC bar at 10:59) / tick. Otherwise 0. On such a d with t_j >= 11:14, a missing bar or a change of instrument_id means no trade at t_j | K6-011 P-K6-011-a, P-K6-011-d; K6-037 P-K6-037-a; K6-015 P-K6-015-b ("persist for approximately ten minutes"); K6-014 P-K6-014-a (spike of five to six minutes) | 11:14 CT (close of the bar at 11:13) |
| KF3 | zs_ret30 | (close of the ZS bar at t_j - 1 - open of the ZS bar at t_j - 30) / 0.0025, in ZS ticks. Both bars must exist with one ZS instrument_id, else no trade at t_j | K6-029 P-K6-029-c ("Efficient return correlations increase right after announcement and remain about 50% higher than regular days till the end of the session"), P-K6-029-b | ZS bars closed <= t_j |
| KF4 | lim_pos | (close of the ZC bar at t_j - 1 - S(c, d-1)) / L(ZC, d), where c is the contract traded at t_j and L the limit in force on d (expanded where in force). It lies in [-1, 1] inside the band. If no limit applies to c on d (P-K6-048-d), no trade at t_j | K6-036 P-K6-036-a (tighter limits raise the chance an extreme move ends at the limit, "Magnet"), P-K6-036-b (volume concentrates before a limit hit); K6-047 P-K6-047-a, P-K6-047-b; K6-048 P-K6-048-a to P-K6-048-d (levels, resets, expansion) | S(c, d-1) after d-1's settlement (C10); L from E.2's dated limit table, known before d; bar closed <= t_j |
| KF5 | prev_limit | +1 if S(c, d-1) = S(c, d-2) + L(ZC, d-1); -1 if S(c, d-1) = S(c, d-2) - L(ZC, d-1); else 0. c is the contract traded on d; settlements exist for every listed month | K6-002 P-K6-002-a, P-K6-002-b, P-K6-002-c; K6-003 P-K6-003-a | after d-1's settlement (C10), before d's first decision |
| KF6 | cp_ge_chg | On the first grain trade date whose session opens after an EC-CP release (the 19:00 CT open that follows the 15:00 CT release): the national corn condition's (good + excellent) percentage this week minus the same last week, in percentage points, both as printed in that release's corn condition table (not a later revision). 0 on every other trade date, and when the release carries no corn condition table | K6-034 P-K6-034-a (released after the session, "before the subsequent trading session opens"), P-K6-034-b (the reaction is in the close-to-open return), P-K6-034-c (strongest in July and August); K6-039 P-K6-039-a; K6-049 P-K6-049-b | 15:00 CT on the release date (ESMIS txt; free, dated, 2019-2026 history, C9d) |
| KF7 | pre_usda | 1 if the next trade date in EC-CAL is an EC-USDA date, else 0 | K6-015 P-K6-015-b ("the last trading session before USDA announcements as traders adjust their market exposure"); K6-043 P-K6-043-a ("informed trading exists ... before the release date") | schedule known in advance |

- **Decision window [W0, W1] = [08:44, 12:44] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 08:44, 09:14, ..., 12:44, which is 9 a day. W1 + h = 13:14 <= F = 13:18.
  - **Fills:** by D15.3's convention a position runs from the open of t_j + 1 to the open of
    t_j + 30. Entry fills fall at :45 and :15, exit fills at :14 and :44.
  - **Why this window.**
    - It starts 14 minutes after the 08:30 reopen that follows the grain pause, which is the D9.4
      gapped-market caution. It ends with an exit at 13:14, the ports' C-2 exit.
    - The 11:00 release lies strictly inside the position interval [10:45, 11:14], and the 13:00 FOMC
      statement inside [12:45, 13:14]. No ML fill lands in [11:00, 11:02) or [13:00, 13:02).
    - The window is the day session only: the overnight session's coverage is unmeasured, and the
      crush cointegration "fades away during session 1" (P-K6-026-c).
  - **Why h = 30.**
    - The report variance difference "is significant in the second period for 30 to 40 minutes after
      the release" (P-K6-014-d).
    - "observed returns correlation fades in about 30 minutes after the announcement" (P-K6-029-c).
    - "the higher volatility did not persist much beyond 60 minutes" (P-K6-030-a).
    - h = 15 would split the release response window (P-K6-014-a, P-K6-015-b). h = 60 or 120 would
      leave at most 4 or 2 decisions in the 4.8-hour grain session and fold the release into a longer
      interval.
- **Expected rows:** 9 x the eligible research-window trade dates. That is about 300 dates, less
  roll-blackout, vendor-degraded and early-halt dates (D15.3), and less the 20-date warm-up of B4:
  roughly 2,000-2,500 rows. E.2 gives the exact count.
- **Expected entries:** at most 9 per day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it). Failing the D5 screen
  puts it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 13:14.
  2. Order type: market (D15.6).
  3. D9.4: at most 9 entries a day, 30-minute holds, no stops or brackets. No fill in a release
     minute.
  4. Star: none.
  5. News: q = 1 lot, not the full maximum. A position may span the 11:00 release or the 13:00
     statement. The 11:14 and 13:14 exits pay D8's event-window cost.
  6. D9.5a: no fill in a guard window.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: the harness guard and the release residual (C13).
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:** ohlcv-1m of ZC and ZS: the research window for training and tuning, the
  confirmation window for the frozen model. The member-level coverage check covers 08:45-13:14.
  External: EC-USDA, EC-CAL, EC-CP, EC-LIM.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K6-crush3-01 | The soybean crush spread as published: long or short ZS, ZM and ZL together, open to close, after a GPM gap (K6-001 P-K6-001-a, P-K6-001-f; a 10-12-9 contract ratio, 31 contracts, per the log) | D9.5 / D9.6 (position) | No K6 product has a Topstep-permitted micro (F1). Three full-size legs are 3 lot-equivalents: over the 1-lot member cap (D9.5) and over the 50K XFA's 2-lot maximum (F5.2). The same mechanism is carried single-leg by K6-crushgap-01 |
| X-02 K6-crush2-01 | Two-leg crush or oilshare spreads (ZS against ZM or ZL; ZL against ZM), including a minute-scale version of the day-session cointegration (K6-026 P-K6-026-a, P-K6-026-c) | D9.5 | Two full-size legs are 2 lot-equivalents, over the 1-lot cap. That is also the full XFA maximum, which F6.3 forbids trading into a scheduled major release, and every grain report day is one. K6-026 has no trading rule and one year of data (P-K6-026-d) |
| X-03 K6-crushavg-01 | Trade the GPM back toward its 5-day average (K6-008 P-K6-008-a, P-K6-008-b; K6-044 P-K6-044-a) | Rule 1 (evidence, parameters) | Abstracts only. The filter, the holding period and whether the reversion shows within one session are in no passage. The intraday crush reversion is carried by K6-crushgap-01. As a two-leg rule it would also fail D9.5 |
| X-04 K6-surprise-01 | Trade a USDA report by the sign of its surprise (USDA minus trade guess) (K6-010 P-K6-010-a; K6-011 P-K6-011-a; K6-017 P-K6-017-a; K6-027 P-K6-027-a; K6-045 P-K6-045-a) | Rule 3 | The trade guess is a newswire poll: "surveyed by newswire services, such as Thompson/Reuters and Bloomberg" (P-K6-010-e); "aggregated by business intelligence firms Bloomberg LP and LSEG" (P-K6-049-e); "analysts' forecasts published by Bloomberg" (P-K6-045-a). No named, obtainable free historical source was found. With the obtainable proxy (the first minutes' price response), the post-release part is K6-wasdepost-01. The pre-release part, read from price, is K6-wasdepre-01. The release-minute part is X-06 |
| X-05 K6-stocksrev-01 | Fade the Grain Stocks surprise ("the corn market may have read too much into those surprises", K6-010 P-K6-010-c, P-K6-010-d) | Rule 3; rule 1; flat by F | It needs the trade guess. The overreaction is a conjecture inferred from later feed-and-residual revisions, not a price test. Its horizon is later WASDE months (multi-day). An intraday version is [unverified] (log tag) |
| X-06 K6-relmin-01 | A position opened in the release minute or the first minutes after 11:00 (K6-012 P-K6-012-d, P-K6-012-e; K6-014 P-K6-014-a, P-K6-014-e; K6-016 P-K6-016-b; K6-024 P-K6-024-a, P-K6-024-c; K6-020 P-K6-020-b) | D9.5a; D9.4; D9.3(c) | No fill is simulated in [T, T + 2 min). The first minutes are a speed race: "it can still easily be a five-minute delay" to download a report, and a "two-second speed advantage" (P-K6-012-d, P-K6-012-e). That is the gapped-market case of D9.4, where a bar-open fill is not a real fill. The first-minute overreaction pattern is "difficult to establish" (P-K6-014-e). A hold matching the 5-10 minute spike (P-K6-014-a, P-K6-020-b) would breach the 10-minute mean hold |
| X-07 K6-cpfade-01 | Fade soybeans' Crop Progress response during the next day session (K6-034 P-K6-034-d) | Rule 1 (evidence) | The main result is a null for the day session: "Significant results could not be found for the open-to-close return of the report-release trading day" (P-K6-034-b). The overreaction hint is one subsample, and the author warns "these ex post results do not necessarily imply that a profitable trading strategy could have been developed" (P-K6-034-d). The release (15:00 CT) now meets the 19:00 CT evening session, so the documented close-to-open response is today an overnight move the program cannot hold. The condition change survives as feature KF6 of K6-ml-01 |
| X-08 K6-lvrpt-01 | HE or LE traded at the next morning's open after Cattle on Feed, Hogs and Pigs or Cold Storage (14:00 CT; K6-018 P-K6-018-a, P-K6-018-e; K6-040 P-K6-040-a, P-K6-040-b; K6-039 P-K6-039-c, P-K6-039-d) | Rule 1; D9.7; rule 3 | No intraday post-open mechanism is logged. "very few reports had a statistically significant impact on the cattle markets ... Market reaction to USDA information was even less common in lean hog markets" (P-K6-018-e). The volatility impact "largely disappeared after 2000" (R-K6-046). "28.5% of the days with Hogs and Pigs report releases were subject to price limit moves" (P-K6-018-c), so a report-morning entry often meets the 2% band. The surprise needs proprietary polls |
| X-09 K6-expsales-01 | Trade the Thursday 07:30 CT Export Sales release (K6-041 P-K6-041-a; K6-049 P-K6-049-d) | Rule 1; D9.1; D9.3 | No price-response passage was logged (the only export study, R-K6-029, is daily and pre-electronic). Fills are possible only from 07:32 (D9.5a) to 07:43 (the pre-pause exit, D9.1): at most an 11-minute position at the thin end of the overnight session, whose coverage is unmeasured. The daily flash-sales release at 08:00 CT falls inside the pause (P-K6-041-b) |
| X-10 K6-settle-01 | Fade the move into the settlement minute (K6-007 P-K6-007-a, P-K6-007-b, P-K6-007-c; K6-009 P-K6-009-a to P-K6-009-c) | Flat by F; rule 1 | The reversal is measured from settlement to the next open, an overnight hold the XFA flat rule and the grain pause forbid. The effect belonged to pit-only settlement: "the percentage of reversals falls from 57.3% under the old regime to 48.7% under the new" (P-K6-007-c). The whole 2019-2026 window is under the new regime |
| X-11 K6-magnet-01 | Trade toward the limit as the price approaches it ("the probability of limit moves conditional to extreme movements increases when limit levels are tighter", K6-036 P-K6-036-a; P-K6-036-b) | D9.7; D9.4 | The payoff lies inside the 2% band where the program must not hold a position. Volume collapses at the limit (P-K6-036-b), the gapped-market case. The limit state survives as feature KF4 of K6-ml-01 |
| X-12 K6-lockday-01 | Trade on the limit day itself, or at the reopening after a lock, by the options-implied futures price (K6-002 P-K6-002-d; K6-035 P-K6-035-a, P-K6-035-b) | D9.7; data; D9.4 | On the lock day the price is in the band. Options data are not in the plan, and on locked days the options-implied price is "only a biased, inefficient, and highly noisy estimate" (P-K6-035-b). The reopening after a lock is the gapped, illiquid moment (P-K6-035-a). The next-day part is K6-limitcont-01 |
| X-13 K6-idxroll-01 | Commodity-index roll in grains and livestock: nearby against deferred during the GSCI or DJ-UBSCI roll, or front-running it (K4-034 P-K4-034-a, P-K4-034-b; K4-035 P-K4-035-b, P-K4-035-c; K4-036 P-K4-036-b, P-K4-036-d, all [K6]) | Flat by F; D9.5; rule 1 | The effects are multi-day, settlement-to-settlement nearby-minus-deferred differentials; front-running holds for weeks. Two legs fail D9.5, and deferred months are not in the data plan. The ag differentials are "on order of the typical bid/ask spreads" (P-K4-036-b): for example "Corn C 48 ... 0.0012*", "Soybeans S 48 ... -0.0016" (P-K4-036-d). The pooled effect is "never significant once we adjust the standard errors" (P-K4-034-a). A single-leg intraday version has no passage |
| X-14 K6-biofuel-01 | ZL on the trade date after an EPA or CARB biofuel-policy event, in the direction of the event response: "Post-Announcement-Leak Drift" (K6-032 P-K6-032-a, P-K6-032-b; kept in K6 by lead ruling) | Rule 3; rule 1 | Abstract only. The 36 events "including ... news 'leaks' from media sources with early information access" were not retrieved, and leaks have no named, obtainable, timestamped historical source. The day-session share of the next-day +0.62% is unreported. The source sample (2021-2025) overlaps the confirmation and research windows, so a confirmation pass would partly re-test the discovery sample. A re-specified member is sketched for the lead in section 7, item 9 |
| X-15 K6-flashrev-01 | Fade flash moves in ZC and HE (K6-025 P-K6-025-a) | Rule 1 (evidence against) | The abstract finds that flash events "are heavily influenced by unanticipated changes in fundamentals that may lead to a new equilibrium price", which argues against a reversal. It is recorded as counter-evidence in K6-ovr-01 |
| X-16 K6-mktstruct-01 | Trade with the day's directional-trader share (K6-045 P-K6-045-a, P-K6-045-c) | Rule 3 | The trader-group shares come from confidential CFTC transaction data, and the surprise from Bloomberg surveys |
| X-17 K6-chpmi-01 | Grains traded on the Chinese PMI surprise (K3-007 P-K3-007-j [K6]) | Rule 1 (null); rule 3 | "Agricultural commodities used in the food industry (corn, soybeans and wheat) show no significant reaction to the PMI news" (P-K3-007-j). The surprise needs a proprietary consensus |
| X-18 K6-ovnrev-01 | Overnight-to-intraday reversal on grains (K3-040 [K6]) | Rule 1 | Title only; content [unverified]. A single-product gap fade is D.1 family D-H4, which D6 does not port |

---

## 3. Beyond budget (lead decides)

None. The log supports 5 new members inside the budget of 11. These candidates were considered and not
written; none is a budget overflow:
- **ZW, ZM and ZL versions of K6-wasdepre-01, and ZS and ZW versions of K6-wasdepost-01.** Topstep's
  Crop Production row lists all five grains, but the pre-release drift source is corn and soybeans
  (P-K6-027-a) and the lingering source is corn (P-K6-037-a). Extending them is an untested
  inference. Cost: up to +5 trials.
- **Grain Stocks, Prospective Plantings and Acreage days in the two WASDE members.** These releases
  move markets most (P-K6-018-f), but the drift and lingering sources are WASDE-specific. Cost: no
  extra trials, but the event set would widen away from the evidence.
- **A fade variant of K6-limitcont-01**, trading against the opening move on the day after a limit
  close. It would rest on the -0.61 arithmetic from P-K6-002-d, whose same-sample premise is not
  stated. Cost: +7 trials, and it is correlated with K6-limitcont-01's sign check, which already
  reports the direction.
- **A month filter for the report members** (K6-013: quiet WASDE months, P-K6-013-a). It describes
  balance-sheet changes, not price responses, and would add an untraced parameter.

---

## 4. Routed to K8

| Source (log section 4) | Legs | One phrase |
|---|---|---|
| CME OpenMarkets 2023, "Are Soybean Oil and Crude Oil Playing a Game of Tag?" | ZL (K6) and CL (K4) | soybean oil against crude, lead-lag |
| CME Articles 2021, "Energy Demand Revives Soybean Complex Trading Dynamics" | ZS, ZL, ZM (K6) and energy (K4) | biofuel demand links |
| CME education, "Relationship Between Major Grain Commodity Benchmarks and Equities Prices During Economic Downturns" | ZC, ZS, ZW (K6) and equity indices (K1) | grains against equities in downturns |
| JCM 2024 (Cao, Heckelei, Ionici, Robe), "USDA reports affect the stock market, too" | USDA grain reports (K6) and equities (K1) | one cluster's announcement moving another's product |
| CFTC OCE 2024, "Do Agricultural Swaps Co-Move with Equity Markets? Evidence from the COVID-19 Crisis" | ag swaps (K6) and equities (K1) | crisis co-movement |
| CFTC OCE, "Convective Risk Flows in Commodity Futures Markets" | VIX (K1) and commodity positions including ags (K6) | risk flows conditioned on VIX, daily |
| Agribusiness 2026 (Zhang), "Spillover Effects of Energy and Grain Futures Volatility: WTI, Natural Gas, and EUA Futures on U.S. Wheat, Corn, and Soybean Markets" | CL, NG (K4) and ZC, ZS, ZW (K6) | energy-to-grain volatility spillover |
| arXiv 1209.0900 and arXiv 1210.6080 | ethanol and crude (K4) and corn (K6) | biofuel links |

K4's catalog routes three more K4-K6 items (JFM 2010 corn-crude spillover; J. Agricultural Economics
2025 WTI and grains; arXiv 1209.0900, the same item as above). K6-032 (EPA and CARB) is **not** routed:
it stays in K6 by lead ruling (STATE 01:23) and is excluded here on its own merits (X-14).

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K6.md section 3 and every `[K6]`-tagged
passage elsewhere.

| Item | Disposition |
|---|---|
| K6-001 Rechner, Poitras | Used: K6-crushgap-01 (P-a, b, d, e, f; quality tells stated). The published three-leg spread is excluded, X-01 |
| K6-002 Janardanan, Qiao, Rouwenhorst | Used: K6-limitcont-01 (P-a to P-f, with P-d as counter-evidence); K6-ml-01 prev_limit. The options-implied lock-day signal is excluded, X-12 |
| K6-003 Park | Used: K6-limitcont-01 (P-a, supporting; abstract only); K6-ml-01 prev_limit |
| K6-004 Brorsen (blocked) | Insufficient evidence: title only, with no content retrieved. Not used |
| K6-005 = K5-023 Martell, Trevino | Duplicate registry line (the claim is K5-023). Title only, retrieved by neither reader: insufficient evidence |
| K6-006 Silveira et al. | Insufficient evidence for a member: WASDE raises corn's intraday volatility and volume with no direction (P-a, P-b). Supports the event set and C12 |
| K6-007 Onur, Reiffen | Excluded, X-10 |
| K6-008 Simon | Excluded as its own member, X-03. Supporting evidence (reversion) in K6-crushgap-01 |
| K6-009 Peterson | Excluded, X-10 (settlement-construction facts; P-c on livestock settlement noted) |
| K6-010 Irwin, Good | Excluded, X-04 and X-05. P-e is cited for rule 3 |
| K6-011 Adjemian et al. | Used: K6-wasdepre-01 (response direction, P-a); K6-wasdepost-01 (counter-evidence, P-d); K6-ml-01 usda_resp; C13 and the D9.7 notes (P-b, P-e, a confirmation-window date, no parameter taken). The surprise version is excluded, X-04 |
| K6-012 Irwin | Used for timing (P-b 11:00 CT since January 2013; P-c livestock after the close) in C9. The release-minute trade is excluded, X-06 (P-d, P-e) |
| K6-013 Janzen | Not used as a filter (section 3): it describes balance-sheet changes by month, not price responses |
| K6-014 Joseph, Garcia | Used: K6-wasdepre-01 (exit timing, P-a; efficiency scope, P-b); K6-wasdepost-01 (counter-evidence, P-b); K6-ovr-01 skip rule (P-b); K6-ml-01 h (P-d) and usda_resp (P-a). The first-minute pattern is excluded, X-06 (P-e) |
| K6-015 Lehecka, Wang, Garcia | Used: K6-wasdepre-01 (pre-release adjustment and ten-minute persistence, P-b); K6-wasdepost-01 (counter-evidence, P-b); K6-ml-01 pre_usda and usda_resp |
| K6-016 Adjemian, Irwin | Used for timing context in X-06 (P-b: volatility "dissipates within the space of a few trading minutes"). No direction; no member |
| K6-017 Karali et al. | Used: release-time history in C9 (P-b). Supporting for the surprise-response direction in K6-wasdepre-01 (P-a). Daily: not intraday-feasible as measured |
| K6-018 Isengildina-Massa et al. | Used: C9 livestock times (P-a) and Grain Stocks times (P-b); limit frequencies (P-c) in K6-limitcont-01 and C13; X-08 (P-e); report importance (P-f) in section 3 |
| K6-019 Indriawan, Martinez, Tse | Context only: the 2018 end of media early access precedes the window, and market-quality proxies are "not statistically different before and after" (P-b). No member |
| K6-020 Bunek, Janzen | Insufficient evidence for a member: a KC wheat volatility fact (P-a, P-b). Used in X-06 |
| K6-021 Wang, Garcia, Irwin | Cost input: corn spread about one tick (P-c) and wider on report days (P-b). A cross-check for D8, used in C12 |
| K6-022 Frank, Garcia | Cost input for LE and HE (P-b, P-c): a cross-check for D8. No member |
| K6-023 Couleau, Serra, Garcia | Context: the night-session cancellation (P-d) is used in C3. The open's quote concentration (P-c) supports K6-limitcont-01's 08:45 entry. The noise horizon (P-a, P-b) is a reason no new member reads a sub-15-minute livestock signal |
| K6-024 Couleau, Serra, Garcia | Supports D9.5a, C12 and X-06 (jumps cluster at the release, P-a, P-c). No member |
| K6-025 He, Serra, Garcia | Counter-evidence in K6-ovr-01 (P-a); excluded as a member, X-15 |
| K6-026 Zhou et al. | Used: K6-crushgap-01 (P-b, P-c; P-d and P-e as limits); K6-wasdepre-01 (P-b); K6-ml-01 window (P-c). The two-leg version is excluded, X-02 |
| K6-027 Aitkulova, Balsamo, Seamon | Used: K6-wasdepre-01 (P-a); K6-ml-01 usda_phase. The surprise version is excluded, X-04 |
| K6-028 Zhu et al. | Used: supporting evidence in K6-wasdepost-01 (P-b) |
| K6-029 Bian, Serra, Garcia | Used: K6-wasdepre-01 entry timing (P-a); K6-ml-01 usda_phase (P-a), zs_ret30 (P-b, P-c) and h (P-c) |
| K6-030 Kauffman | Used: K6-ml-01 h (P-a) |
| K6-031 Hu, Mallory, Serra, Garcia | Not a mechanism: a roll-timing input for E.2 (section 7, item 10) |
| K6-032 Avileis, Swanson | Excluded, X-14 (stays in K6 by lead ruling; section 7, item 9) |
| K6-033 Li, Wang, Diersen | Context in K6-ovr-01 (P-a). No rule; news is matched by day only (P-b) |
| K6-034 Lehecka | Used: K6-ml-01 cp_ge_chg (P-a, b, c). The fade member is excluded, X-07 (P-b, P-d) |
| K6-035 He, Serra | Used: K6-limitcont-01 (entry delay and counter-evidence, P-a). X-12 (P-b) |
| K6-036 Fontinelle, Janzen | Used: K6-ml-01 lim_pos (P-a, P-b). The member is excluded, X-11 |
| K6-037 Arnade, Hoffman, Effland | Used: K6-wasdepost-01 (P-a, c, d); K6-ml-01 usda_resp; release-time history (P-b) |
| K6-038 WASDE page | Used: C9a (P-a, P-b) |
| K6-039 NASS calendar | Used: C9d (P-a); X-08 (P-c, P-d); Crop Production time (P-b) |
| K6-040 NASS PFEI schedule | Used: C9a (P-a, P-b); X-08 |
| K6-041 FAS Export Sales | Used in X-09 (P-a, P-b) |
| K6-042 AMS livestock reports | Not used: the afternoon cash reports come after the livestock close, and the morning times are [unverified] |
| K6-043 Zhang | Used: K6-wasdepre-01 (P-a, supporting); K6-ml-01 pre_usda |
| K6-044 Mitchell | Supporting for reversion (P-a); X-03. No member |
| K6-045 Du, Kane | Excluded, X-16; P-a is cited for rule 3 in X-04 |
| K6-046 | Crude only, K4's region (log section 5). Not a K6 source; not used |
| K6-047 CME price limits | Used: C10, C13, K6-limitcont-01, K6-ml-01 lim_pos (P-a, P-b, P-c) |
| K6-048 CME limit FAQ | Used: C10, C13, K6-limitcont-01, K6-crushgap-01's linkage note, K6-ml-01 (P-a to P-d) |
| K6-049 CME USDA reports guide | Used: C1 and C9 (P-a to P-d); rule 3 (P-e) in X-04 |
| K6-050 CME crush reference guide | Used: K6-crushgap-01 GPM weights (P-a, P-b) |
| K6-051 CME Asian-hours soybeans | Context: overnight ZS liquidity (P-a to P-c). No overnight member is written (C5), so it is not used |
| K3-007 [K6] Baum, Kurov, Wolfe (P-K3-007-j) | Excluded, X-17 (null for corn, wheat and soybeans) |
| K3-040 [K6] Kosowski et al. | Excluded, X-18 (title only) |
| K4-016 (registry tags K4, K6) | Rejected by K4 (R-K4-038: a multi-day ETF hold). There is no [K6] passage and it is not intraday-feasible. Not used |
| K4-034 [K6] Dubois, Maréchal | Excluded, X-13 (P-a, P-b) |
| K4-035 [K6] Mou | Not intraday-feasible (multi-week calendar spreads, P-b, P-c); X-13 |
| K4-036 [K6] Stoll, Whaley | Excluded, X-13 (P-b, P-d) |
| K4-039 (registry tags K4, K5, K6) | Rejected by K4 (R-K4-040: non-public CFTC positions). Not used |
| R-K4-063 (K4 log) | A K6-region title rejected by K4 (delivery convergence). Not a passed item. Delivery-period mechanisms need positions into delivery (compare R-K6-012, R-K6-055) |
| K5-023 Martell, Trevino | Title only, not retrieved: insufficient evidence |
| K5-029 [K6] Borgards, Czudaj, Hoang (P-a, P-b, P-d) | Used: K6-ovr-01. P-c ([K5]/[K4]) is used for the method only |
| K5-030 Gu, Kurov, Stan | Unread by K5, and K6 coverage is [unverified]. Not used |
| R-K6-001 to R-K6-070 | Rejected by the reader. Not used, except as cited: R-K6-006 and R-K6-032 in CP1, R-K6-029 in X-09, R-K6-046 in X-08 |
| Partition seeds with no passed item | Weather-forecast updates (R-K6-011 daily, R-K6-027 seasonal, R-K6-049 satellite); wheat against corn and hogs against cattle (R-K6-014 is daily cointegration; no intraday source); first notice day and delivery (R-K6-012, R-K6-055). No member |

**Correlated members, flagged for the lead's Tier-A accounting (not duplication).**
- K6-limitcont-01's trades are a same-direction subset of K6-cp3-01's (section 7, item 8).
- K6-wasdepre-01 and K6-wasdepost-01 on ZC meet at 11:15: one exits and the other may enter. They are
  separate hypotheses: the pre-release drift, and continuation after the release.
- K6-ml-01 carries the release, limit and Crop Progress states as features, which overlaps the
  information of the hand-written members by design (D15).

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all seven admitted) |
|---|---|---|---|
| K6-cp1-01 | ZC, ZW, ZS, ZM, ZL, HE, LE | 1 | 7 |
| K6-cp2-01 | ZC, ZW, ZS, ZM, ZL, HE, LE | 1 | 7 |
| K6-cp3-01 | ZC, ZW, ZS, ZM, ZL, HE, LE | 1 | 7 |
| K6-crushgap-01 | ZS only (lead ruling; ZM, ZL removed) | 1 | 1 |
| K6-limitcont-01 | HE, LE (lead ruling; grains removed) | 1 | 2 |
| K6-wasdepre-01 | ZC, ZS | 1 | 2 |
| K6-wasdepost-01 | ZC | 1 | 1 |
| K6-ovr-01 | EXCLUDED by the lead (01:52) | - | 0 |
| ~~K6-ml-01~~ [excluded, U6] | ZC (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **39** = 21 port + 17 new + 1 ML. In general 4E + (a_ZS + a_ZM + a_ZL) + (a_ZC + a_ZS) + a_ZC + (a_ZW + a_ZC + a_ZS + a_ZL) + a_ZC. The cuts in section 7, item 7 would bring it to 28 |

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **Spreads in K6 cannot meet D9.5.**
   - No K6 product has a Topstep-permitted micro, so every inside-K6 spread (crush, oilshare,
     wheat-corn, hogs-cattle) needs at least 2 full-size lots. That exceeds the 1-lot-equivalent member
     cap; a three-leg crush exceeds even the XFA maximum (X-01, X-02).
   - K6-crushgap-01 is the single-leg reading, an explicit inference.
   - Options: keep it on all three legs (3 trials), keep it on ZS only (1 trial; the most liquid leg,
     ADV 302,997), or drop it.
2. **D9.7 inputs are not in the spend plan.**
   - Encoding D9.7 for any K6 member, ports included, needs:
     - the official daily settlement of each vehicle contract on every date (C10);
     - CME's historical limit tables, with the semi-annual grain resets, the expanded state and its
       linkages, the spot-month and pre-FND exemptions, and livestock limit changes.
   - The settlements are paid, for example the GLBX.MDP3 statistics schema. They are not in D13 and
     need a quote in E.1. No free source with 2019-2026 history was found.
   - A bar-close proxy would misclassify limit closes, because the settlement is not the last trade
     (K6-009).
   - K6-limitcont-01 and K6-ml-01 (lim_pos, prev_limit) read the same inputs.
3. **The D9.7 residual across the 11:00 release.**
   - A position held through a release that jumps into the 2% band is exited at the first bar D9.5a
     allows (11:02 at the earliest). It is therefore "held" inside the band for up to about 2 minutes.
   - This affects CP2 and CP3 on grains, K6-crushgap-01, K6-wasdepre-01, K6-limitcont-01 (grains) and
     K6-ml-01.
   - Should this be accepted, or should grain members be flat across 11:00 on EC-USDA dates? For the
     ports that would be a D6 change.
4. **The arithmetic of D9.7.** "within 2% of the day's limit price" could mean 2% of the price level
   (|P - U| <= 0.02 U) or 2% of the limit amount. For corn, whose limit is 7% of a 45-day average
   price (P-K6-048-a), the first reading blocks from about 70% of the limit move and the second only
   at the limit itself: roughly an order of magnitude apart. E.2 or the lead fixes the reading before
   any bar is read.
5. **CP2 on livestock on FOMC days.** An entry intent on the 12:59 bar fills at 13:00, which D9.5a
   defers to 13:02, leaving one bar to F = 13:03 and breaking D9.3(b). A harness rule would fix it
   (skip an entry whose deferred fill leaves fewer than three bars to F). This is a D6 or D9 matter.
6. **CP1 on livestock** has no overnight component: the first bar is 08:30 (C3). The D6 text is
   applied as written.
7. **Trial count 39.** Possible cuts, each the lead's call:
   - K6-limitcont-01 to HE and LE only, where limit moves are 2 to 4 times as frequent as in crops
     (P-K6-018-c), so the grain trials are likely "inconclusive by design": -5.
   - K6-ovr-01, which has no grain-specific result and counter-evidence in K6-025: -4.
   - K6-crushgap-01 to ZS only: -2.
   - With all three cuts: 28.
   - The two WASDE members trade on about 5% of dates (C11) and are likely null at eps or
     inconclusive (lead ruling Q4: the power check decides).
8. **K6-limitcont-01 is nested in K6-cp3-01.** A limit close has CLV of 1 or 0. It is a distinct
   hypothesis (the limit itself, P-K6-002-a) but a correlated one in Tier A.
9. **K6-032 (EPA and CARB) is excluded (X-14).** If the lead wants it, a re-specified member (1 trial)
   would be:
   - event set: EPA Renewable Fuel Standard volume rules and small-refinery-exemption decisions, and
     CARB Low Carbon Fuel Standard rulemaking releases, each dated by the agency's own press release
     or Federal Register record (the lead names the sources);
   - signal: the ZL move from the close of the 13:14 bar on the last trade date before the event date
     to the 08:30 open of the first trade date after it;
   - trade: that trade date's day session, from 08:45 to 13:14, in the signal's direction.

   It would test the post-announcement drift without the leak events, which the source includes.
10. **Roll convention for the K6 vehicles (E.2).**
    - Grain limits are removed on the business day before first notice day (P-K6-048-d).
    - Nearby price-discovery leadership ends when the nearby's volume share falls below 50%, "about
      2-3 weeks before expiration in corn and 5-6 weeks before expiration in live cattle"
      (P-K6-031-a).
    - A convention that rolls before those points keeps D9.7 defined and trades the leading contract.
    - K6-crushgap-01 accepts month mismatches across the crush legs.
11. **Source samples inside the confirmation window.** These matter for an edge claim only:
    - K6-027 (window [unverified], 2026), which K6-wasdepre-01 rests on;
    - K6-028 (2013-2020);
    - K6-033 (2013-2022);
    - K6-011 (August reports 2009-2019);
    - K5-029 (2019-11..2020-06), which K6-ovr-01 rests on.

    No parameter was taken from any confirmation-window date. A pass by K6-wasdepre-01 or K6-ovr-01
    would partly re-test its source's own sample.
12. **Entries one minute after the 08:30 reopen** (CP3 and K6-crushgap-01 on grains). They are read
    here as ordinary market orders, not D9.4 "reckless trades in gapped markets". The lead confirms
    that reading.
13. **E.2 checks named in this catalog:**
    - (a) tick-size and price-unit history, 2019-2026 (C7);
    - (b) grain and livestock session hours and early closes, 2019-2026 (D10);
    - (c) EC-USDA from the yearly schedules and the ESMIS record, with the drop rule; ESMIS shows no
      October 2025 WASDE or Crop Progress (C9a);
    - (d) the Crop Progress corn-condition table format across 2019-2026, parsed from each release as
      published (C9d, KF6);
    - (e) settlements and the historical limit table (C10);
    - (f) member-level coverage for 08:45-13:14 (ML) and CP1's reading of the 19:00 CT bar;
    - (g) legs bought for non-admitted exposures (C8).
14. **Seeds with no member:** weather-forecast updates, wheat against corn, hogs against cattle,
    Export Sales, and livestock reports (section 5 and X-08, X-09). Livestock is covered only by the
    ports and K6-limitcont-01.
15. **Registry hygiene** (from the reader): K6-005 duplicates K5-023; K6-046 is a crude-only K4-region
    line; K6-019's registry line carries only a partial DOI, and the log resolves it to
    10.1016/j.jcomm.2020.100149.

---

# Cluster K7

# Stage E.0 hypothesis catalog, cluster K7 (crypto: MBT traded; MET as a signal leg only)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K7-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U1: MET stays OUT; it may serve only as a signal leg under D9's member-level coverage check.
> **K7 after the decisions: 6 active members, 6 confirmation trials** (3 new + 3 core ports; 3 port + 3 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K7-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:41 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any product (MBT, MET, BTC, spot bitcoin, ETFs) existed on this machine. It uses only these
product-specific numbers:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- calendar metadata: MBT contract terms, UK and US holiday lists, BLS release dates, FOMC dates, time
  zones.

No price level, range or volatility of any product is used or assumed anywhere below. The arithmetic
in ticks and dollars (C11) uses only tick values, fees and the design's $85 bar.

**Inputs read in full:**
- reports/stage_e0_research_K7.md (sections 0 to 5).
- `[K7]`-tagged passages in the other logs: none exist. `grep -n '\[K7\]' reports/stage_e0_research_K*.md`
  finds only the K7 log's own header sentence. The K8 log's rows F35 to F46 are K8's dispositions of
  K7's flags, not `[K7]` passages (section 4).
- reports/stage_e0_source_registry.jsonl (the 43 K7 lines, and K8-004, which is tagged K7).
- docs/STAGE_E_DESIGN.md D1 to D15, with the 21:12 and 21:52 amendments; the lead rulings in
  reports/stage_e0_STATE.md (21:12, 21:52, 21:55, and the 01:40 note that event windows are
  half-open, [release, release + 30 min)).
- reports/stage_e0_partition.md; reports/stage_e0_topstep_facts.md (F1 to F12);
  reports/stage_e0_liquidity.json (MBT and MET rows); reports/stage_e0_symbology.json (MBT.v.0).
- reports/stage_d1f_confirmation_list.md 2.1 A3; strategy/research/b_reference_breakout/
  h1_friction_aware_opening_range_breakout.py (the exit count of CP2); docs/SCREENING.md (roll
  blackout = "The splice trade date plus the 2 sessions before it").
- reports/stage_e0_catalog_K4.md, reports/stage_e0_catalog_K3.md, and reports/stage_e0_catalog_K2.md
  C9 (EC-FOMC and EC-NFP sources, reused), for format only.

**Official pages fetched in this task** (curl, 2026-09-24 01:44-01:52 PDT). Files are saved under the
scratchpad `fetch/` folder with the prefix `k7cw_`, never in the repository. They were fetched only to
confirm session times, methodology and data-source availability. No mechanism research was done.
- Wayback CDX listing of cmegroup.com/media-room/press-releases/2026/* (92 captures). It lists the two
  releases below.
- CME Group press release, 19 Feb 2026, "CME Group to launch 24/7 cryptocurrency futures and options
  trading on May 29" (Wayback capture 20260219141120 of
  https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html).
  Verbatim quotes:
  - "Beginning Friday, May 29 at 4:00 p.m. CT, CME Group Cryptocurrency futures and options will
    trade continuously on CME Globex with at least a two-hour weekly maintenance period over the
    weekend."
  - "All holiday or weekend trading from Friday evening through Sunday evening will have a trade date
    of the following business day, with clearing, settlement and regulatory reporting processed the
    following business day as well."
- CME Group press release, 1 June 2026 (Wayback capture 20260602010915 of
  https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html).
  Verbatim: "today announced it launched 24/7 trading for Cryptocurrency futures and options. The
  expanded trading hours, which went live on Friday, May 29, ..."
- https://www.cfbenchmarks.com/data/indices/BRR (HTTP 200). Verbatim: "If you require access to real
  time or historic data for this index to power a product or service or are interested in licensing the
  index for the creation of a financial product, investment fund or derivative instrument please
  contact". No free historical download is offered on the page.
- https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles (HTTP 200).
  Documentation only; no candle was requested. Verbatim:
  - "Historic rates for a product."
  - granularity "{60, 300, 900, 3600, 21600, 86400}"
  - "The maximum number of data points for a single request is 300 candles."
  - "time bucket start time".
- BLS release archives https://www.bls.gov/bls/news-release/cpi.htm and .../ppi.htm return HTTP 403
  to curl. The Wayback captures 20260830144214 (CPI) and 20260821235014 (PPI) list 326 CPI and 327 PPI
  release files, named by date. 14 of each fall inside the research window, including the irregular
  2025 dates (for example CPI 2025-10-24 and PPI 2025-11-25).

**Read from the shared scratchpad, not fetched by this writer:**
- gov_uk_bank_holidays.json, England and Wales, 2019-2028 (fetched by CatalogWriter-K3).
- blasco.pdf, the K7 reader's copy of K7-005. It was re-read only to trace the length of the expiry
  window. Its method section says: "The first one, D1, takes a value of 1 at the hour of the expiration
  and 0 otherwise. Subsequently D2 takes a value of 1 both at the hour of expiration and 1 h beforehand
  and 0 otherwise".

**Time-zone conversions** were computed locally with Python zoneinfo (the IANA tz database).

---

## 0. Header

| Item | Value |
|---|---|
| Products | MBT (CME Micro Bitcoin, 0.10 bitcoin, CME rulebook chapter 348 per the liquidity JSON). Topstep lists it as "Micro Bitcoin (MBT)*" inside "CME Equity Futures" (F1). MET (Micro Ether) is on the permitted list but out of the traded universe |
| Traded exposure | **bitcoin {MBT}**, the only K7 exposure left after D1. MBT is its only admissible contract: 2026 Jan-Aug ADV 69,615, coverage 0.996 (D1 table) |
| D1 | **D1 applied: MET out** (day-session coverage 0.947 < 0.95; ADV 61,082 passes). MET may appear only as a signal leg that passes D9's member-level coverage check. **No member in this catalog reads MET** (K7-ml-01 explains why) |
| D2 | Vehicle "D2 (chosen in E.2)". The only candidate is MBT at q = 1 (the 1-lot-equivalent cap; Topstep "Micro Bitcoin (MBT): Capped at mini-equivalent lot sizes, not standard micro scaling", F5.4). Bitcoin is traded only if MBT's rho = r_MBT / R* <= 2.0 at q = 1 (measured in E.2). If rho > 2.0, no K7 member trades |
| Members | **7 = 3 new + 3 core ports + 1 ML member.** The budget is 15, so 8 slots are unused (section 3). The cluster is thin, and nothing is padded |
| Trials in N (confirmation) | **7** if D2 admits bitcoin (3 port + 3 new + 1 ML); 0 otherwise |
| ML grid | ~~48 configurations, counted only in the K7 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Starred product | **MBT\*** (F1.9). Its referent is Topstep's "Risk Adjustments: High Risk/High Volatility" page (F12.1). That page bans MBT only in the small Challenge tiers: "In the $3K Challenge, you cannot trade MHG, MET, MBT, or SIL" (the same for the $1.5K Challenge). It sets no MBT restriction for the 50K XFA. The page's volatility caps name energies and metals only, and its CPI-window rules name other products. **For the 50K XFA the star imposes nothing beyond F5.4's mini-equivalent weighting**, so q = 1 MBT = 1 lot-equivalent. Whether a volatility halt of "mini-sized contracts or larger" could reach MBT is [unverified]; that is a deployment question, not a design one |
| 24/7 CME crypto trading | **Verified in this task.** CME's 1 June 2026 release says 24/7 trading "went live on Friday, May 29" (2026-05-29, from 16:00 CT per the 19 Feb release). The K7 log carried this as K7-036, unverified. See the next row and C3 |
| Effect on the windows | **Research window** 2025-04-01..2026-06-19: the program trade dates 2026-06-01..2026-06-19 (15 of about 305, the last three weeks) come after the change. From 2026-05-29 16:00 CT, the MBT data contain weekend bars and weekday 16:00-16:59 CT bars, which did not exist before. Under the program's trade-date convention (C3) none of them belongs to a program trade date, and no K7 member reads them. D2's risk measure (day session) and D8's five cost-sample dates (2025-05-14..2026-04-15) are unaffected. **Confirmation window** (S_X..2024-02-29) and **holdout-2** (2024-04..2025-03) are entirely pre-change. **Forward deployment is entirely post-change**, and TopstepX itself stays closed "Friday close 3:10 PM CT (closed till Sunday at 5:00 PM)" (F4, page read 2026-09-23). A K7 confirmation result therefore describes the pre-change regime (section 7, items 1 to 3) |
| Members that touch the weekend or the Sunday reopen | CME-gap members: **excluded** (X-01, with the brief's reason). CP1's Monday signal and K7-montrend-01 read MBT bars from Sunday 17:00 CT. Each states its definition before and after 2026-05-29; both are identical by the C3 convention |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** Times are America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose
  ts_event (its open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values
  are usable from then on. Eastern times convert to CT by subtracting one hour (the two zones change
  clocks on the same dates). London times are converted per date with zoneinfo. They are not a fixed
  offset, because the UK and US change clocks on different dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine convention of
  D6 and D15). "Market intent on the bar at X" fills at the open of the bar at X + 1 min.
  - **Orders never exceed q.** In the three new members, a change of direction is a flatten followed by
    a new entry, never one 2q order:
    - The flatten intent is emitted on the bar that closes at the decision time and fills at the open
      of the decision-time bar.
    - The entry intent is emitted on the next bar and fills one minute later.
- **C3 Trade date (the program convention, reports/stage_e0_STATE.md).**
  - **Definition:** trade date d = [d-1 17:00 CT, d 16:00 CT). The first bar of trade date d is the
    17:00 CT bar of the previous calendar day (Sunday for a Monday).
  - **Before 2026-05-29:** the definition matches CME's session, with the daily 16:00-17:00 CT break
    and the weekend closure from Friday 16:00 CT to Sunday 17:00 CT (P-K7-033-b; P-K7-002-e).
  - **After 2026-05-29:** CME trades continuously and gives weekend trading "a trade date of the
    following business day" (19 Feb 2026 release). **This catalog keeps the program convention in both
    regimes.** Bars from Friday 16:00 CT to Sunday 17:00 CT, and weekday bars from 16:00 to 16:59 CT,
    belong to no program trade date. No member reads them, and no daily bar includes them.
  - **Consequence:** the first bar of a Monday trade date is the Sunday 17:00 CT bar in both regimes.
    If the lead instead adopts CME's post-change assignment, CP1's Monday signal and the ML member's B2
    on Mondays would start at Friday 16:00 CT and read weekend prices (section 7, item 2).
- **C4 Exclusions for the three new members** (the ports follow D6 as written; the ML member follows
  D15.3). A new member does not trade on:
  - roll-blackout dates (`screen_candidate` with `roll_blackout`: the splice trade date plus the 2
    sessions before it);
  - dates the D10 equity-and-crypto calendar marks as early close or early halt (Family H's "Days with
    early_halt_ct set: no trade");
  - vendor-degraded dates.

  A rule whose required bar is missing, or whose signal bars of one computation carry different
  instrument_ids, treats that signal as 0 (flat). If an exit's named bar is missing, the exit is sent
  on the first later bar, and the engine's forced flatten at F is the backstop. A CME price-limit halt
  shows up as missing bars and is handled the same way.
- **C5 Flat time.** F = 15:08 CT (D9.1). D6 crypto row: O = 08:30, C = 15:00, F = 15:08. MBT itself
  trades until 16:00 CT (before the change) or continuously (after it); TopstepX flattens at 15:10 CT
  (F4). Early-close days: F = the early close minus 15 minutes (D9.1, D9.13).
- **C6 Size.** q = 1 MBT = 1 lot-equivalent (D2 cap; F5.4; D9.6 weight "MBT 1"). This is half the 50K
  XFA's starting 2-lot maximum. No member sizes by signal. At most one position.
- **C7 Tick, fees, epsilon.** From reports/stage_e0_liquidity.json (CME MBT specification page,
  fetched 2026-09-23 20:51 PDT):
  - tick "5.00 (USD per bitcoin)", "$0.50 per contract";
  - contract unit "0.10 bitcoin";
  - listed 2021-05-03.

  Topstep's round turn is $2.82 (F3), which is 5.64 ticks.

  D3's translated bar: eps_bitcoin = floor(85.00 / (1 x 0.50)) = **170 net ticks per contract per
  day**. The operative eps is min(translated, funnel-derived), set in E.2 (D3). E.2 confirms the tick
  was unchanged from 2021-05 to 2026-06 before any bar is read (CP2's buffer and the ML features are in
  ticks).
- **C8 Price data.**
  - **Source:** Databento GLBX.MDP3 ohlcv-1m of MBT. It is paid. D13 quotes K7 at $1.49 (research
    window) + $3.11 (2019-05..2025-03 history) + $1.20 (mbp-1 sample).
  - **History:** the quotes for months before 2021-04 failed with "None of the symbols could be
    resolved" (D13), so MBT history starts at its 2021-05-03 listing.
  - **Continuous series:** MBT.v.0 (volume roll; 62 roll intervals over 2019-05..2026-06 in
    reports/stage_e0_symbology.json, that is, monthly from 2021).
  - **Availability:** a bar is available at its close (C1).
  - **No sealed data is read.** A lookback that would reach a sealed trade date (holdout-2 ends on
    trade date 2025-03-31) counts as missing, so a rule that needs d-1 does not trade on the first
    research trade date.
  - **Expiring contract:** no member holds an expiring MBT contract on its last trading day. If the
    continuous series still holds the expiring month on its final trading day, the splice must fall on
    the next trade date at the latest. The roll blackout (splice date plus the 2 sessions before it)
    then covers that final trading day.
- **C9 Calendars.** All are free, and every rule reads them only as dates and clock times.
  - **EC-CAL.** The D10 equity-and-crypto calendar (trade dates, holidays, early closes and halts),
    built by E.2 from CME schedules. It needs a crypto note for dates after 2026-05-29 (section 7,
    item 1).
  - **EC-MBTX, MBT final trading days and T_exp.**
    - **Rule:** "Trading terminates at 4:00 p.m. London time on the last Friday of the contract month.
      If that day is not a business day in both the U.K. and the U.S., trading terminates on the
      preceding day that is a business day for both the U.K. and the U.S." (P-K7-033-c). Final
      settlement: "the CME CF Bitcoin Reference Rate (BRR) at 4:00 p.m. London time on the expiration
      day" (P-K7-033-d).
    - **T_exp(d):** 16:00 Europe/London on d, converted to CT with zoneinfo. It is normally 10:00 CT,
      and 11:00 CT in the weeks when UK and US clocks differ.
    - **Dates by the rule** (computed here from the gov.uk list and US federal holidays plus Good
      Friday; E.2 confirms each against CME's published MBT contract calendar):
      - Research window, 14 dates: 2025-04-25, 05-30, 06-27, 07-25, 08-29, 09-26, 10-31 (T_exp 11:00
        CT), 11-28, 12-24 (a Wednesday: 26 December is a UK holiday and 25 December a holiday in
        both), 2026-01-30, 02-27, 03-27 (T_exp 11:00 CT), 04-24, 05-29.
      - Confirmation window (2021-05-03..2024-02-29), 34 dates: 2021-05-28 to 2024-02-23, including
        2021-12-30 (a Thursday) and 2022-03-25 (T_exp 11:00 CT).
    - **Availability:** contract terms known in advance.
  - **EC-FOMC.** Scheduled FOMC statement days, reused from reports/stage_e0_catalog_K2.md C9:
    - source https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm plus the historical
      pages;
    - regularly scheduled meetings only;
    - statement at 13:00 CT (Topstep F6 "FOMC Statement | 1:00 PM | All products"; P-K7-029-b
      "14:00 (New York time)");
    - published before each year.
  - **EC-NFP.** BLS Employment Situation release dates (K2 C9: https://www.bls.gov/bls/news-release/empsit.htm),
    08:30 ET = 07:30 CT (Topstep F6 "Unemployment Rate | 7:30 AM | ... MBT, MET").
  - **EC-CPI, EC-PPI.** BLS CPI and PPI release dates from the archive pages above (Wayback captures
    fetched here). The standard 08:30 ET time is [not re-confirmed per release in this task]. E.2
    reads each release file's embargo line and drops any release not published at 08:30 ET.
  - **Availability of release dates.** As used in K7-ml-01 KF1, a release's occurrence on d is known
    at its publication time, 07:30 CT, which is before any K7 decision that reads it.
- **C10 Spot, reference-rate and flow data: none is read by any member.**
  - **BRR and BRRNY values:** historical data require a licence (CF Benchmarks page above), so they
    are not free. The obtainable proxy for the final-settlement price is MBT's own bars, which is what
    K7-expiry-01 trades.
  - **Spot bitcoin minute data:** free through Coinbase's public candles endpoint (1-minute buckets,
    300 per request). How far back 1-minute history goes was not checked in this task.
  - **Offshore perpetual data** (Huobi, OKEx, BitMEX in K7-002): not checked.
  - **Spot-ETF daily flows:** the publication times are unverified (X-03).
- **C11 Frequency and the eps multiple (arithmetic from calendar counts and C7; no price data).**
  - **Size of the windows:** the research window has 319 weekdays (about 305 CME trade dates) and 63
    Mondays. The confirmation window, from MBT's listing, has 739 weekdays and 148 Mondays.
  - **The multiple:** a member that trades on k of about 305 research dates, with zeros on the others
    (D5), needs a net P&L per trading day of about (305 / k) x 170 ticks to reach eps.
    - K7-expiry-01 (k about 12): about 25 x eps per event, about 4,300 ticks, about $2,150 on one MBT.
    - K7-montrend-01 (k about 55): about 5.5 x eps per Monday.

    Both are likely to end "null at eps" or "inconclusive by design" (D4). That is a structural
    outcome (section 7, item 6).
- **C12 Coverage.** D1's coverage figure (0.996) was measured only inside 08:30-15:00 CT on the five
  calibration dates. K7-expiry-01 (from 05:00 or 06:00 CT) and K7-montrend-01 (Sunday 17:00 CT to
  Monday 14:00 CT) trade outside that window, so each depends on E.2's member-level coverage check
  (>= 0.95 in its own window, D9). No fallback window is written (section 7, item 5).
- **C13 Price-limit proximity (D9.7).** MBT carries CME price fluctuation limits. The FAQ describes a

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  dynamic variant "applied in rolling 60-minute look-back periods to establish dynamic lower and upper
  price fluctuation limits" (P-K7-033-e). E.2 reads the MBT rulebook chapter and builds the limit
  table. The liquidity JSON says chapter 348; the K7 log's R-K7-061 looked for "chapter 350".
  Encoded as D9.7: no entry, and an immediate exit, while the price is within 2% of a limit price.
  This catalog assumes no limit is hit.
- **C14 Release minutes and event-window cost.**
  - **Releases concerning MBT:**
    - Topstep's table: the Employment Situation at 07:30 CT and the FOMC statement at 13:00 CT (F6).
    - Named by this catalog's members: CPI and PPI at 07:30 CT (K7-ml-01 KF1).
  - **D8 event-window cost:** fills in [07:30, 08:00) on those release days and in [13:00, 13:30) on
    FOMC days pay the largest bucket (half-open per the 01:40 ruling).
  - **D9.5a guard:** no fill in [release, release + 2 min).
  - **Which members are exposed:** only CP2 can fill inside such a window. Every other member's fill
    times avoid them by construction, as each entry states.

---

## 1. Members

### K7-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K7.
  - **Products read:** MBT only.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits the exposure.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log A10
  and A28), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the trade
    date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the
    signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
    (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
  - **K7 log, recorded as covered by CP1:**
    - K7-011, Shen, Urquhart and Wang, on spot bitcoin: the return from the previous day's close,
      "when the 60-minute break of CME Bitcoin futures trading begins at 5pm EST" (P-K7-011-a), to 30
      minutes after the exchange open "significantly predicts the last half hour with a slope of
      0.968" (P-K7-011-b). This is the same mechanism.
    - The paper's predicted half hour ends at 16:00 CT, after F, so CP1 tests the in-session analogue,
      which the paper did not test.
    - Evidence against it in the same paper: the 10am-4pm re-test is "a lot smaller in magnitude and
      statistical significance" (P-K7-011-e), and breakeven costs are 3 to 10 bps (P-K7-011-d).
    - The momentum half of K7-018 (P-K7-018-a, -c; abstract only) is in the same family.
- **Instantiated with the crypto row (O = 08:30, C = 15:00, F = 15:08):**
  - **Signal:** close of the bar at 08:59 minus the open of the trade date's first bar, which is the
    17:00 CT bar of d-1 (C3).
  - **Entry:** market intent on the bar at 14:29, filling at the 14:30 open, in the signal's
    direction. A zero signal means no trade.
  - **Exit:** market intent on the first bar at or after 14:58, filling nominally at the 14:59 open.
    14:59 is the first second of MBT's daily-settlement minute: "VWAP of CME Globex trades between
    3:59:00 p.m. and 4:00:00 p.m. Eastern Time" (P-K7-033-a).
  - **Holding horizon:** 29 minutes. **Session window:** 14:30-14:59 CT. Flat 9 minutes before F.
  - **Context only:** the holding period lies inside the BRRNY hour, 14:00-15:00 CT, in which "more
    than 20% of a day's notional volume is transacted" (P-K7-038-a).
- **Before and after 2026-05-29 (Monday trade dates):**
  - **Before:** the first bar is the 17:00 CT Sunday reopen bar. The signal starts at that bar's open,
    so the Friday-to-Sunday gap is never part of it.
  - **After:** by C3 the first bar is still the Sunday 17:00 CT bar, now an ordinary bar of continuous
    trading. Weekend bars are not read.
  - **Tuesday to Friday:** unchanged in both regimes (after the change, the 16:00-16:59 CT bars of
    d-1 are not read).
- **Data fields read:** MBT ohlcv-1m open, close and instrument_id (C8). Paid; history from 2021-05-03.
  The first bar is available at 17:01 CT on d-1, and the 08:59 bar at 09:00 CT.
- **Order type:** market. **Sizing:** q = 1 MBT (C6).
- **Parameters:** O+29 min = the 08:59 bar, C-31 min = the 14:29 bar, C-2 min = the 14:58 bar (D6).
  **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date, held 29 minutes. Floor: <= 20
  entries, ok; 2-minute minimum hold, ok; 10-minute mean, ok.
- **Falsification:** the standard condition only (a port; D6 unchanged). UCB95 of the member's mean net
  daily P&L per contract below eps_bitcoin, at >= 80% achieved null power on the confirmation window,
  counts against it.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills. Neither fill is at a reopen or
     release minute, so this is not a gapped-market fill.
  4. Star: MBT\*; nothing applies to the 50K XFA beyond F5.4 (header).
  5. News: 1 lot-equivalent, not the full maximum. No release falls in 14:30-14:59.
  6. D9.5a guard: no fill in a release minute. The FOMC statement at 13:00 CT is before the entry.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research window 2025-04-01..2026-06-19 and confirmation S_X..2024-02-29
  (S_X >= 2021-05-03, D4). No external data.
- **Trials in N:** 1.

### K7-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K7.
  - **Products read:** MBT only.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py, hold_minutes =
  75), as fixed in D6 row CP2 with the 21:12 amendment and the 21:52 buffer ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market
    intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes after
    the fill, or the engine's forced flatten at F if earlier."
  - **K7 log:** K7-022 (Deprez and Frömmel) tests channel-breakout and support-resistance rules among
    75,360 rules on Bitstamp bitcoin (P-K7-022-a). The breakout family on bitcoin is therefore
    **covered by CP2**, with a negative prior:
    - "only 1.68% of the trading rules, on average, outperformed the benchmark in terms of mean excess
      return" (P-K7-022-d);
    - the best portfolios are "not statistically significant" (P-K7-022-b).

    No crypto-specific opening-range source was found (R-K7-053: Fetna's ORB panel is K4-050, with no
    crypto).
- **Instantiated:**
  - **Opening range:** high and low of the bars opening in [08:30, 08:45). Context: this is the
    window of the post-ETF opening volatility spike (P-K7-014-a).
  - **Eligible bars:** those opening in [08:45, 15:00). No entry from 15:00 CT on.
  - **Buffer:** 4 ticks of MBT, the exposure's most active and only contract (D6 ruling of 21:52).
    That is 20.00 in price units (USD per bitcoin), $2.00 per contract.
  - **Entry:** the first eligible bar whose close is >= OR_high + 20.00 buys; the first whose close
    is <= OR_low - 20.00 sells. The intent fills at the next open. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it: the exit intent is
    emitted on the 75th bar after the entry-intent bar and fills at the next open. The engine's forced
    flatten at F = 15:08 applies to fills after 13:53. As in MES's D.1 run, a late break (latest fill
    15:00) is held at most 8 minutes.
  - **Holding horizon:** 75 minutes, less when F binds. **Session window:** 08:46-15:08 CT.
- **Before and after 2026-05-29:** unaffected (it reads only the day session).
- **Data fields read:** MBT ohlcv-1m high, low, close and instrument_id (C8). The range is known at
  08:45 CT.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** OR 15 minutes, buffer 4 ticks (20.00), hold 75 minutes (D6, a literal port).
  **Grid:** none.
- **Expected entries and hold:** at most 1 per day. The hold is 75 minutes, or 8 to 75 minutes when F
  binds. Floor: ok, since the minimum hold of 8 minutes is >= 2. The 10-minute mean is checked at
  screening.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: forced flatten at 15:08 at the latest.
  2. Order type: market.
  3. D9.4: one trade a day; no stops.
  4. Star: as CP1.
  5. News: 1 lot-equivalent. A position may be open at the 13:00 FOMC statement, which F6.3 allows
     below full maximum size.
  6. D9.5a guard: an entry whose fill would land in [13:00, 13:02) on an FOMC day fills at the 13:02
     open. Fills in [13:00, 13:30) pay D8's event-window cost (C14).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research and confirmation windows.
- **Trials in N:** 1.

### K7-cp3-01 (core port CP3, prior-close location)
- **Cluster** K7.
  - **Products read:** MBT only.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6), as
  fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L over
    [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H.
    CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent
    on the O bar of day d. Exit: first bar at or after C-2 min."
  - **K7 log:** no crypto-specific prior-close-location source. The daily-bar constructions in the log
    are of other kinds:
    - K7-040's MAX(10), an overnight hold;
    - K7-041's N-day high around holidays, close-to-close.

    Both are infeasible (section 2). No K7 item is covered by CP3.
- **Instantiated:**
  - **Daily bar:** O_d is the open of the 08:30 bar. H and L are taken over the bars opening in
    [08:30, 15:00). C_d is the close of the 14:59 bar (the settlement-minute bar, P-K7-033-a).
  - **Complete day:** the 08:30 and 14:59 bars exist, the date is not an early halt, and all its bars
    in [08:30, 15:00) carry one instrument_id.
  - **Instrument guard:** d-1's bar carries the instrument_id of day d's 08:30 bar.
  - **d-1:** the previous complete trade date in EC-CAL. For a Monday that is Friday's bar in both
    regimes, since no weekend bar enters any daily bar (C3).
  - **CLV:** computed with Range[d-1] > 0. CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict, as H6).
  - **Entry:** market intent on the 08:30 bar of d, filling at the 08:31 open.
  - **Exit:** market intent on the first bar at or after 14:58, filling nominally at the 14:59 open.
  - **Holding horizon:** about 388 minutes. **Session window:** 08:31-14:59 CT.
- **Data fields read:** MBT ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar is
  complete at 15:00 CT on d-1.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** CLV cuts 0.2 and 0.8; lookback 1 complete bar (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 388 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: ok.
  4. Star: as CP1.
  5. News: the position holds through FOMC statements at 1 lot-equivalent, not the full maximum
     (D9.5). The 07:30 releases come before the entry.
  6. D9.5a guard: the fills at 08:31 and 14:59 are not in any release minute.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research and confirmation windows.
- **Trials in N:** 1.

### K7-expiry-01 (long MBT in the five hours before the BRR final-settlement time on MBT's last trading day)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source covers 2017-12 to 2020-11, overlapping MBT's confirmation window where MBT exists.]
- **Cluster** K7.
  - **Products read:** MBT; EC-MBTX; EC-CAL.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** New to the program. Settlement-window and expiry effects are the product's cluster's
  (partition section 4). It is also a family E calendar event with an hourly horizon.
  - **The evidence:** around the CME bitcoin futures expiry, spot bitcoin shows abnormal positive
    returns in the hours before expiry. "a clear effect on prices at the maturity time and 5 h prior to
    the expiration time in all the exchanges under analysis. Returns are significantly higher than the
    mean return at the 1% significance level" (P-K7-005-b).
  - **The authors' attribution:** "Typically, this effect is attributed to the unwinding of short
    arbitrage positions" (P-K7-005-c).
  - **The clock:** final settlement is the BRR at 4:00 p.m. London (P-K7-005-a, P-K7-033-d). The BRR is
    the equal-weighted average of twelve 5-minute volume-weighted medians of constituent spot trades
    from 3:00 to 4:00 p.m. London (P-K7-019-a, -b). The BRR window "sees the greatest number of
    transactions" (P-K7-032-b).
  - **Transfer to MBT (reasoned, untested):** MBT is priced off the same spot market and absorbs spot
    moves within minutes at most. CME absorbed shocks "between 4 and 5 minutes" in 2019-2020
    (P-K7-002-b), and MBT led Binance by fractions of a second in 2024 (P-K7-025-b). A spot move over a
    five-hour window therefore appears in MBT's price. On a traded expiry day the vehicle holds the
    next month's contract (C8), which tracks spot plus a basis. That basis changes slowly relative to
    a five-hour move (a judgment).
- **Conflicting evidence, stated in advance:**
  - **Sign:** K7-004 (daily spot bars cut at 00:00 UTC) finds that after the October 2021 BITO launch
    "the pattern in the daily returns after the BITO ETF introduction (2021-2024) is reversed,
    especially on days preceding the expiration and on the expiration day itself" (P-K7-004-b). MBT's
    whole history (from 2021-05) falls in that later period. K7-005's own sample is 2017-12..2020-11
    (P-K7-005-e): pre-MBT and pre-spot-ETF.
  - **Last hour:** the pooled robustness finds the effect "about 5 h before expiration, although not
    in the last hour" (P-K7-005-d). The per-exchange result says "The strongest effect is reflected in
    D2 and D1" (P-K7-005-b).
  - **Multiplicity:** "we have finally run 576 models" (log, K7-005 quality tells).
  - **Other exchanges' expiries:** CBOE expiries show "scarce" effects (P-K7-005-f).
- **Rule:**
  - **Dates:** each EC-MBTX final trading day d that is a full trade date (C4).
  - **Clock:** T_exp(d) = 16:00 Europe/London on d, in CT (C9): 10:00 CT normally, 11:00 CT in the
    weeks when UK and US clocks differ.
  - **Entry:** market intent BUY on the bar at T_exp - 301 min, filling at the open of the bar at
    T_exp - 300 min (05:00 CT, or 06:00 CT).
  - **Exit:** market intent on the bar at T_exp - 2 min, filling at the open of the bar at T_exp - 1
    min (09:59 CT, or 10:59 CT).
  - **Holding horizon:** 299 minutes. **Session window:** 05:00-09:59 CT (06:00-10:59 CT in
    mismatch weeks). Flat hours before F.
- **Before and after 2026-05-29:** unaffected. The rule reads no weekend or reopen bar. 2026-05-29
  is both an EC-MBTX date and the day 24/7 trading began, but the change started at 16:00 CT, after
  the window. The BRR method is in version 17.4, dated 24 August 2026 (P-K7-019-d).
- **Data fields read:**
  - **MBT ohlcv-1m open and instrument_id (C8):** paid; history from 2021-05-03. The bars are
    available at their close.
  - **EC-MBTX:** the rule text P-K7-033-c, plus the gov.uk England-and-Wales holidays (free,
    2019-2028) and US holidays (EC-CAL). Known in advance.
  - **Time zones:** tz database, free. Known in advance.

  The rule reads **no BRR value** (licensed, C10) and no spot data.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:**
  - **Direction long:** P-K7-005-b, -c.
  - **Window start at T_exp - 300 min:** "5 h prior" (P-K7-005-b); "about 5 h before expiration"
    (P-K7-005-d). The paper's cumulative dummy D5 covers "the hour of expiration" and the 4 hours
    before (its method section, quoted in the preamble). This catalog reads that as [T_exp - 5 h,
    T_exp]. The paper's hour-labelling convention is not stated in the text read [unverified].
  - **Exit at T_exp - 1 min (a judgment):** it keeps the whole position inside the documented window
    and off the settlement instant. The last hour is kept despite P-K7-005-d, because the per-exchange
    result puts the strongest effect there (P-K7-005-b).

  **Grid:** none.
- **Expected entries and hold:**
  - **Research window:** 1 entry per surviving EC-MBTX date, out of 14 dates. 2025-11-28 and
    2025-12-24 are likely D10 early-close dates [E.2 confirms], which leaves about 12, less any
    roll-blackout dates.
  - **Confirmation window:** 34 dates, less early closes and roll blackouts.
  - **Hold:** 299 minutes. Floor ok.
  - **Roll blackout:** an expiry day survives the blackout only if the MBT.v.0 splice came on or
    before the Thursday of that week (C8). E.2 reports how many survive. If none survive, the member
    has no trade dates, and the lead decides before screening (section 7, item 8).
  - **Frequency:** about 25 x eps per event (C11).
- **Falsification:** the standard condition. No member-specific check. The competing sign from K7-004
  is recorded above, before any data.
- **Topstep check:**
  1. Flat by F: last fill 09:59 CT (10:59 CT).
  2. Order type: market.
  3. D9.4: one trade per event day. The entry is not at a reopen, a gap or a release minute. The exit
     is before the BRR window closes. No stops.
  4. Star: as CP1.
  5. News: the position may hold through a 07:30 CT release on d at 1 lot-equivalent (allowed; F6.3
     bars only full maximum size).
  6. D9.5a guard: no fill in [07:30, 07:32) or [13:00, 13:02). No fill in a C14 event window.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:**
  - MBT ohlcv-1m, research and confirmation windows. The member-level coverage check covers
    [T_exp - 300 min, T_exp - 1 min] on EC-MBTX dates, which lies outside D1's measured window (C12).
  - Calendars EC-MBTX and EC-CAL.
- **Trials in N:** 1.

### K7-rev2h-01 (two-hour reversal in the MBT day session)
- **Cluster** K7.
  - **Products read:** MBT; EC-CAL.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of D.1 family C (short-horizon reversal) at family G's coarser bars. The
  evidence is bitcoin-specific (partition rule 6). D6's core set does not port family C, so this is
  not covered by a port.
  - **The evidence:** spot bitcoin returns show significant negative first-order autocorrelation at
    1-, 2- and 4-hour horizons, beyond what microstructure explains: "significant levels of negative
    autocorrelation found for returns calculated on intervals as wide as one, two and even four hours
    cannot usually be attributed to microstructural components" (P-K7-012-a). The values are "1 hour
    -0.0557 ... 2 hours -0.0858 ... 4 hours -0.0564 ... 1 day -0.0071 0.8047" (P-K7-012-b).
  - **The source's rule:** "it bets on the market (goes long) if the last price movement was large and
    negative, and against the market (goes short) if the movement in the last period was large and
    positive. The trade is then closed after a single time unit has passed" (P-K7-012-c). The headline
    run uses 2-hour bars and a zero threshold (P-K7-012-f).
  - **Transfer to MBT (reasoned, untested):** MBT prices spot within minutes at most (P-K7-002-b;
    P-K7-025-b), so a two-hour autocorrelation in spot is present in MBT.
- **Conflicting evidence:**
  - The source sample is 2015-03..2018-06 on one exchange, almost all before CME futures
    (P-K7-012-e), with fees excluded and no out-of-sample test (log quality tells).
  - K7-042's intraday trend-following ensemble earned a gross Sharpe of about 1.6 over 2018-2025
    (P-K7-042-a): the opposite bet. That source also calls US Sunday morning mean-reverting
    (P-K7-042-c).
  - K7-018 finds both momentum and reversal, depending on state (P-K7-018-a, -c).
  - K7-011 finds anti-persistence of the second-to-last half hour (P-K7-011-f), the same sign at 30
    minutes.
  - K7-022's technical rules mostly fail after costs (P-K7-022-b, -d).
- **Rule:**
  - **Blocks:** B1 = [08:30, 10:30), B2 = [10:30, 12:30), B3 = [12:30, 14:30), in CT.
  - **Decision at 10:30:** r1 = close of the 10:29 bar - open of the 08:30 bar. Target = -sign(r1)
    x q; 0 if r1 = 0.
  - **Decision at 12:30:** r2 = close of the 12:29 bar - open of the 10:30 bar. Target = -sign(r2)
    x q.
  - **Orders (C2):**
    - If the target equals the current position, hold.
    - Otherwise, if a position is open, the flatten intent is on the bar at the decision time - 1 min
      (it fills at the decision-time open).
    - If the target is nonzero, the entry intent is on the decision-time bar (it fills one minute
      later, at 10:31 or 12:31).
  - **Final exit:** market intent on the 14:29 bar, filling at the 14:30 open.
  - **Missing data:** a missing endpoint bar or an instrument change between endpoints sets that
    target to 0 (C4).
  - **Holding horizon:** 119 or 120 minutes per block, up to about 239 minutes if the second target
    agrees. **Session window:** 10:31-14:30 CT. Flat 38 minutes before F.
- **Before and after 2026-05-29:** unaffected (day session only).
- **Data fields read:** MBT ohlcv-1m open, close and instrument_id (C8). The latest input is the bar
  closing at the decision time.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:**
  - **Block 120 minutes:** the strongest autocorrelation (P-K7-012-b) and the headline bar size
    (P-K7-012-f).
  - **Threshold 0:** P-K7-012-f.
  - **Hold one block:** P-K7-012-c.
  - **Anchor 08:30 (a judgment):**
    - it is D6's O for crypto and the window where D1 measured coverage at 0.996;
    - it keeps every fill at :30 or :31, off the 13:00 FOMC minute and the 14:59 settlement minute;
    - its third block ends at 14:30, 38 minutes before F.

  **Grid:** none.
- **Expected entries and hold:** at most 2 entries per day (<= 20); each position is held >= 119
  minutes. Floor ok.
- **Falsification:** the standard condition only.
- **Topstep check:**
  1. Flat by F: last fill 14:30.
  2. Order type: market.
  3. D9.4: at most 2 trades a day, 2-hour holds, no stops, no gapped fills.
  4. Star: as CP1.
  5. News: the B3 position spans the 13:00 FOMC statement at 1 lot-equivalent (allowed).
  6. D9.5a guard: the fills at 10:30, 10:31, 12:30, 12:31 and 14:30 are not in any release minute
     or any C14 event window.
  7. Position limit: <= 1 lot-equivalent (the order never exceeds 1, C2).
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research and confirmation windows.
- **Trials in N:** 1.

### K7-montrend-01 (Sunday-evening trend window: hourly time-series momentum on the Monday trade date)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source covers 2018-2025, overlapping the confirmation window.]
- **Cluster** K7.
  - **Products read:** MBT; EC-CAL.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of D.1 family C (intraday trend and momentum), limited to a family A/E clock
  window specific to bitcoin. It is new to the program as an MBT window.
  - **The evidence:** an ensemble of high-frequency trend-following models on bitcoin "delivers
    strongly positive returns starting on Sunday at around 7:00 PM New York time, with performance
    remaining elevated for roughly the next 24 hours into Monday. Notably, this upswing closely aligns
    with the Monday open of Asian cash equity markets" (P-K7-042-b).
  - **Robustness in the source:** the effect "becomes substantially more pronounced in the latter
    subsample" (after mid-2020, P-K7-042-d). The ensemble is long-short and volatility-targeted
    (P-K7-042-e), with a gross Sharpe of about 1.6 (P-K7-042-a).
  - **Feasibility:** Sunday 18:00 CT to Monday 14:00 CT lies inside one TopstepX trading day ("Sunday
    open | 5:00 PM CT", "Weekday close | 3:10 PM CT", F4) and one program trade date (C3). No position
    is held past a daily flatten.
- **Conflicting evidence:**
  - K7-012's negative 1-hour autocorrelation (P-K7-012-b) makes the opposite bet at the same horizon.
  - Concretum's result is gross of fees, and its models and parameters are undisclosed.
  - The Sunday-evening seasonality was found by inspecting a figure, with no test statistic (log
    quality tells).
- **Before and after 2026-05-29.** The rule reads only MBT bars opening at or after Sunday 17:00 CT,
  the first bar of the Monday trade date (C3).
  - **Before the change** (Monday trade dates up to 2026-05-25): the Sunday 17:00 CT bar is CME's
    reopen bar. The first signal (the 17:00-17:59 hour) starts at that bar's open, so the
    Friday-to-Sunday gap is never in a signal. The first fill is at 18:01 CT, one hour after the
    reopen, never at the reopen.
  - **After the change** (from 2026-06-01): the same clock bars are ordinary bars of continuous
    trading. Weekend bars before Sunday 17:00 CT are not read.
  - **Why the mechanism does not depend on CME's weekend closure:** the source attributes the effect
    to the Monday Asian cash open (P-K7-042-b) and measures it on bitcoin itself. The venue is not
    stated in the text read [unverified]; bitcoin itself trades continuously.
  - **The rule is identical in both regimes.** The first hour after a pre-change CME reopen may still
    behave differently from the same hour after the change. The confirmation window is entirely
    pre-change (header; section 7, item 3).
- **Rule:**
  - **Dates:** trade dates d that are Mondays and full trade dates (C4). A Monday holiday with an
    early halt does not trade.
  - **Decision times, 20 of them:** Sunday 18:00, 19:00, 20:00, 21:00, 22:00, 23:00; Monday 00:00,
    01:00, ..., 13:00 (CT).
  - **Signal at each decision time t:** s_t = sign(close of the bar at t - 1 min - open of the bar at
    t - 60 min). If either bar is missing, or the two carry different instrument_ids, then s_t = 0
    (C4).
  - **Orders (C2):**
    - If a position is open and its sign differs from s_t (including s_t = 0), a flatten intent on
      the bar at t - 1 min fills at the open of the bar at t.
    - If s_t is nonzero and the position is then flat, an entry intent in direction s_t on the bar at
      t fills at the open of the bar at t + 1 min.
    - If s_t equals the open position's sign, hold.
  - **Final exit:** market intent on Monday's 13:59 bar, filling at the 14:00 open.
  - **Holding horizon:** each position is held from an entry at t + 1 min to at least the next
    decision (>= 59 minutes). **Session window:** Sunday 18:01 CT to Monday 14:00 CT. Flat 68 minutes
    before F.
- **Data fields read:** MBT ohlcv-1m open, close and instrument_id (C8). The inputs are available at
  the close of the bar at t - 1 min.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:**
  - **Start at Sunday 18:00 CT:** "Sunday at around 7:00 PM New York time" (P-K7-042-b); 19:00 ET =
    18:00 CT in all weeks (C1).
  - **Last decision Monday 13:00 CT, flat at 14:00 CT (a judgment):** F = 15:08 cuts the source's
    roughly 24-hour window, and 20 decisions is D9.3(a)'s maximum of 20 entries a day.
  - **Lookback 60 minutes and decision step 60 minutes (a judgment):**
    - the source's models are undisclosed "high-frequency trend-following models" (P-K7-042-e);
    - one-hour time-series momentum is the simplest trend rule at the resolution the source reports
      its clock in ("around 7:00 PM", "roughly the next 24 hours", P-K7-042-b);
    - it is also the horizon of K7-012's opposite evidence (P-K7-012-b), so the member bets directly
      on which of the two holds in this window.
  - **Threshold 0.**

  **Grid:** none.
- **Expected entries and hold:**
  - At most 20 entries per Monday trade date, none on other days. Each position is held >= 59 minutes.
    Floor: (a) ok, (b) ok, (c) ok.
  - **Research window:** 63 Mondays, less four with likely early halts (2025-05-26, 2025-09-01,
    2026-01-19, 2026-02-16, [E.2 confirms]) and less roll blackouts: about 50 to 55.
  - **Confirmation window:** 148 Mondays, less the same exclusions.
  - **Frequency:** about 5.5 x eps per traded Monday (C11).
- **Falsification:** the standard condition only.
- **Topstep check:**
  1. Flat by F: last fill 14:00 Monday.
  2. Order type: market.
  3. D9.4: at most 20 trades a day, hourly holds, no stops or brackets. No fill in the first 60
     minutes after the Sunday 17:00 CT reopen (before the change), so there are no "reckless trades
     in gapped markets to profit from stray fills" [F7.2].
  4. Star: as CP1.
  5. News: 1 lot-equivalent. A Monday 07:30 CT release is held through at 1 lot (allowed).
  6. D9.5a guard: fills are at hh:00 or hh:01. None falls in [07:30, 07:32) or in the half-open
     event window [07:30, 08:00): 08:00 is outside it.
  7. Position limit: <= 1 lot-equivalent (the order never exceeds 1, C2).
  8. Price limit: C13.
- **Data needed:**
  - MBT ohlcv-1m from Sunday 17:00 CT to Monday 14:00 CT on Monday trade dates, research and
    confirmation windows. The full-session ohlcv-1m purchase in D13 already contains these bars.
  - The member-level coverage check covers [Sunday 17:00, Monday 14:00) CT, which lies outside D1's
    measured window (C12).
  - D8's cost buckets for Sunday evening are calibrated on Tuesday evenings (section 7, item 9).
- **Trials in N:** 1.

### K7-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**
- **Traded vehicle: the bitcoin exposure {MBT}**, the contract chosen by D2 in E.2 (MBT is the only
  admissible one).
  - **Reason:** it is the only traded K7 exposure (D1), and every intraday item in the K7 log concerns
    bitcoin.
  - **No fallback:** if D2 does not admit bitcoin, K7 has no traded exposure and no ML member.
- **Products the features read:** MBT only, plus the calendars EC-CAL, EC-MBTX, EC-FOMC, EC-NFP,
  EC-CPI and EC-PPI (C9).
  - **Why MET is not read:**
    1. MET's day-session coverage is 0.947 (D1 table). A MET leg would very likely fail D9's
       member-level check (>= 0.95 in the member's own window), which would exclude the whole ML member
       before screening.
    2. D13 buys no MET history.
    3. The log's inside-crypto evidence runs from bitcoin to ether, "BTC leads ETH price adjustment"
       (P-K7-021-b), so a MET feature has no logged predictive direction for MBT (X-12).
  - **Why no spot, BRR or ETF-flow feature:** none is in the data plan. BRR history is licensed (C10),
    and ETF-flow publication times are unverified (X-03).
- **Cluster features.** There are 7; with D15.4's B1 to B5 that makes 12. Throughout, t_j is the
  decision time, "the bar at t_j - 1" is the last bar closed at t_j, and tick = 5.00 (MBT).

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | usrel_day | 1 if a BLS Employment Situation, CPI or PPI release was published at 08:30 ET (07:30 CT) on d (EC-NFP, EC-CPI, EC-PPI); else 0 | K7-026 P-K7-026-a, P-K7-026-b (bitcoin's 30-minute response to inflationary surprises); K7-023 P-K7-023-a, P-K7-023-b, P-K7-023-c (activity bursts and a negative return component at US release times); K7-031 P-K7-031-b, P-K7-031-c (US news drives BTC jumps; the unemployment rate is named); K7-003 P-K7-003-c (futures lead more "around macroeconomic surprises"); Topstep F6 (07:30 CT release lists MBT) | 07:30 CT on d, before W0 = 09:30 |
| KF2 | fomc_phase | 0 if d is not an EC-FOMC statement day; 1 if it is and t_j < 13:00 CT; 2 if it is and t_j >= 13:00 CT | K7-029 P-K7-029-a, P-K7-029-b, P-K7-029-c (volatility and volume jump in the first hour after the 14:00 ET statement; placebo-controlled); K7-018 P-K7-018-a (intraday predictability changes on FOMC days); Topstep F6 | schedule known in advance; depends only on the clock |
| KF3 | expiry_phase | 0 if d is not an EC-MBTX final trading day; 1 if it is and t_j < T_exp(d); 2 if it is and t_j >= T_exp(d) (T_exp from C9) | K7-005 P-K7-005-a, P-K7-005-b, P-K7-005-d; K7-033 P-K7-033-c, P-K7-033-d; K7-019 P-K7-019-b | contract terms known in advance |
| KF4 | dow | weekday of d: 0 = Monday, ..., 4 = Friday | K7-042 P-K7-042-b, P-K7-042-d (Monday window); K7-038 P-K7-038-b (weekly Friday BFF settlement to BRRNY); K7-040 P-K7-040-c (returns differ by night of the week); K7-015 P-K7-015-b (a Friday effect) | calendar known in advance |
| KF5 | ret60 | (close of the bar at t_j - 1 - open of the bar at t_j - 60) / tick. Both bars must exist with one instrument_id, else no trade at t_j | K7-012 P-K7-012-a, P-K7-012-b (1-hour autocorrelation -0.0557); K7-042 P-K7-042-b, P-K7-042-e (hourly trend window); K7-018 P-K7-018-c | bars closed <= t_j |
| KF6 | ret120 | (close of the bar at t_j - 1 - open of the bar at t_j - 120) / tick. Both bars must exist with one instrument_id, else no trade at t_j | K7-012 P-K7-012-b (2-hour autocorrelation -0.0858, the strongest), P-K7-012-f | bars closed <= t_j (at t_j = 09:30 the earlier bar is the 07:30 bar) |
| KF7 | open30 | (close of the 08:59 bar - open of the 08:30 bar on d) / tick. Both bars must exist with one instrument_id, else no trade on d | K7-014 P-K7-014-a, P-K7-014-b (post-ETF volatility spike and wider tails in 08:30-09:00 CT, "the only window surviving multiple testing correction"); K7-011 P-K7-011-b, P-K7-011-c (the first half hour predicts the last) | 09:00 CT on d, before W0 |

- **Decision window [W0, W1] = [09:30, 13:30] CT; horizon h = 60 minutes.**
  - **Decision times:** t_j = 09:30, 10:30, 11:30, 12:30, 13:30, which is 5 a day. W1 + h = 14:30 <=
    F.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 min to the open of
    t_j + 60. Every fill is at :31 (entry) or :30 (exit).
  - **Why h = 60:** the logged intraday return evidence for bitcoin is at one to two hours:
    - K7-012's autocorrelation at 1 h and 2 h (P-K7-012-b);
    - K7-042's hourly trend window (P-K7-042-b);
    - K7-029's first post-FOMC hour (P-K7-029-a);
    - K7-024's 1-2 hour flow horizon (P-K7-024-a), a feature not used here (X-07).

    h = 30 matches only K7-011's half-hour construction, whose target window lies after F (covered by
    CP1), and it doubles the round trips per hour of exposure. h = 120 leaves 2 decisions a day in the
    window.
  - **Why this window:**
    1. **It starts at 09:30,** so the 08:30-09:00 opening spike, whose tails widen (P-K7-014-b), is
       never an entry interval. Its move is still available as KF7.
    2. **It stays inside D1's measured day session (0.996).** Volume and volatility are concentrated
       in European and North American hours (P-K7-013-a), which avoids the overnight coverage risk of
       C12.
    3. **The :30 grid keeps every fill off the scheduled minutes:**
       - the 13:00 FOMC statement, which the 12:30 position spans;
       - the 10:00 or 11:00 CT BRR expiry time;
       - the 14:59 settlement minute;
       - the 07:30 releases.

       No ML fill lands in a release minute or a C14 event window, which is the gapped-market case of
       D9.4.
- **Expected rows:** about 5 x the eligible research-window trade dates, where eligible dates are:
  - about 305 trade dates,
  - less about 45 roll-blackout dates (15 monthly splices x 3),
  - less about 8 early-halt and early-close dates,
  - less the 20-date warm-up of B4. That warm-up lies inside the research window, since holdout-2 is
    sealed (C8).

  That is roughly 1,100-1,200 rows. E.2 gives the exact count.
- **Expected entries:** at most 5 per day (<= 20), each held 59 minutes. Floor ok by construction.
- **Falsification:** the standard condition: UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it. Failing the D5 screen puts
  it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 14:30.
  2. Order type: market (D15.6).
  3. D9.4: at most 5 entries a day, 59-minute holds, no stops or brackets, no fill in a release or
     reopen minute.
  4. Star: as CP1.
  5. News: q = 1 lot-equivalent, not the full maximum. The 12:30 position spans the FOMC statement.
  6. D9.5a guard: never triggered by construction.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.

  Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as for every ML member.
- **Data needed:**
  - MBT ohlcv-1m. The research window trains and tunes; the confirmation window scores the frozen
    model.
  - The member-level coverage check covers 09:31-14:30 CT. Features also read the 07:30 CT bar (KF6
    at 09:30) and the trade date's first bar (B2). A missing bar means no trade at that t_j.
  - External: EC-CAL, EC-MBTX, EC-FOMC, EC-NFP, EC-CPI, EC-PPI.
- **Before and after 2026-05-29:** every feature is a clock or calendar value or an MBT day-session
  bar, except B2, which reads the trade date's first bar: Sunday 17:00 CT for Mondays in both regimes
  under C3 (section 7, item 2). No weekend bar is read.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K7-gap-01 | Trade MBT after the Sunday 17:00 CT reopen on the weekend move, following or fading the "gap" between the Friday close and the Sunday open (K7-036 P-K7-036-b; weekend spot volatility "approximately 75% of weekday levels", P-K7-036-c) | CME weekend closure; D9.4; rule 1 | **Depends on CME's weekend closure, announced to end 2026-05-29 (K7-036, unverified); not deployable if in effect; E.1 may revive it only if the closure is confirmed to persist.** Update from this task's fetch: CME's 1 June 2026 release states the 24/7 hours "went live on Friday, May 29". The closure has ended, so nothing is left to revive. The design had two more problems. First, the signal needs weekend spot prices (free Coinbase candles would serve, C10). Second, the first fills after a reopen are the "reckless trades in gapped markets to profit from stray fills" case of D9.4 [F7.2]. The log also found no study of the gap's direction ("No academic study of the CME weekend gap itself was found", log container 2) |
| X-02 K7-spotlead-01 | Trade MBT in the direction of a price move on spot or offshore venues, which CME absorbs in "between 4 and 5 minutes" (K7-002 P-K7-002-a, P-K7-002-b, P-K7-002-c, P-K7-002-d; K7-001 P-K7-001-a) | D9.3; D9.4; rule 1 (conflicting evidence) | The documented edge ends within 5 minutes of the shock, so a one-minute-bar rule filling at the next open keeps at most a few minutes. Holding to the 10-minute mean-hold floor, D9.3(c), means holding beyond the documented horizon, and the edge sits at Topstep's "durations measured in seconds, not minutes" line [F7.3]. Evidence from the MBT era is the other way: CME "leads price discovery" (P-K7-021-b); "CME bitcoin futures have consistently led price formation" (P-K7-006-b); "the futures market generally leads spot" (P-K7-003-b); and MBT itself led Binance by 0.055 to 0.15 seconds in 2024 (P-K7-025-b, -c). K7-003 calls the direction specification-sensitive (P-K7-003-a). Data: spot minute bars are free (C10); offshore perpetual history was not checked |
| X-03 K7-etfflow-01 | Trade MBT in the day session in the direction of the prior day's net flow into US spot bitcoin ETFs (K7-020 P-K7-020-a, P-K7-020-b; K7-027 P-K7-027-a) | Rule 3 (availability timestamp); D4 (window) | (a) When the day-d flow becomes public relative to 08:30 CT on d+1 is not stated ("[unverified], which decides feasibility", log K7-020). No archive of publication times was found, so a rule reading flow(d-1) cannot be shown to be free of look-ahead. (b) The flows exist only from January 2024 (P-K7-020-d window). The confirmation window ends 2024-02-29, so it holds only about 40 ETF-era trade dates, and the member would be "inconclusive by design". (c) The source itself finds that "individual flow shocks reverse significantly" once future flows are controlled (P-K7-020-c). Revival would need a timestamped flow source and a confirmation design that covers the ETF era |
| X-04 K7-cpisurp-01 | Trade MBT after the 07:30 CT CPI or PPI release, signed by the inflation surprise: "Bitcoin price decreases by 24 bps (t-statistics 2.44)" per 1 SD (K7-026 P-K7-026-a) | Rule 3; D9.5a; rule 1 | The surprise needs the survey consensus the source uses (a Bloomberg survey, log K7-026 mechanism), which is proprietary, and no obtainable history was named. The documented response is contemporaneous, in a window "10 minutes before ... 20 minutes after" the release (P-K7-026-b), and the first two minutes are unfillable under D9.5a. A post-release drift is untested. The sample is 2013-2021, before the ETFs. The release calendar enters K7-ml-01 as KF1 |
| X-05 K7-relshort-01 | Short MBT around the 07:30 CT US release, following the eigen-signal that "points out to the occurrence of negative log-returns during that period" (K7-023 P-K7-023-c) | Rule 1 | It is descriptive: a correlation-matrix component on Binance 2020-2022 (P-K7-023-d), with no conditional-mean test and no window or event list. "12:30 UTC" equals 08:30 ET only while US summer time is in force; in winter 08:30 ET is 13:30 UTC (arithmetic), so the timing is ambiguous. It enters K7-ml-01 as KF1 |
| X-06 K7-basisfb-01 | Five-minute momentum or reversal on MBT, switched by the level or change of the futures-spot basis (K7-007 P-K7-007-a, P-K7-007-b); the crash-state basis of K7-008 (P-K7-008-b) | Rule 1; not intraday-feasible (K7-008) | K7-007 is abstract only. The quantiles and state definitions that switch the sign ("When the basis declines by varying magnitudes across quantiles", P-K7-007-b) are not given, so no parameter can be traced. A five-minute horizon also sits against the 10-minute mean-hold floor. K7-008 is two-legged arbitrage held to expiry on CBOE futures (P-K7-008-a), and the spot leg is not tradable on Topstep |
| X-07 K7-onchain-01 | Buy MBT for 1 to 2 hours after large USDT net inflows to exchanges, "US$ 100 million of USDT net inflows predict ... 0.065% of BTC return in the next hour" (K7-024 P-K7-024-a, P-K7-024-c) | Rule 3 | Exchange net inflows need exchange-wallet attribution from an on-chain data vendor (log: "on-chain data vendor dependence (a data source this program does not hold)"). No free, timestamped historical series was named. BTC's own flows "generally lack predictive power" (P-K7-024-d), and USDT is insignificant beyond 2 hours (P-K7-024-b) |
| X-08 K7-brrny-01 | A directional MBT trade in the BRRNY hour, 14:00-15:00 CT, the benchmark of "six out of the 10 new spot bitcoin" ETFs with "more than 20% of a day's notional volume" (K7-038 P-K7-038-a, P-K7-038-d; K7-019 P-K7-019-b, P-K7-019-c; K7-034 P-K7-034-b, P-K7-034-c) | Rule 1 | Only volume and replication facts are logged. The methodology anticipates even spreading of hedge flow ("transacting Y/K units of the cryptocurrency during each partition", P-K7-019-c), and no return or direction for the hour is documented. The ETF regime is absent from the confirmation window (as X-03). BRRNY values are licensed (C10). The clock enters the ML member through B3 and KF4 |
| X-09 K7-tas-01 | Trade the MBT settlement minute (14:59-15:00 CT, P-K7-033-a) through the offsetting flow of TAS counterparties (K7-037 P-K7-037-a, P-K7-037-b) | Rule 1; D9.3 | TAS size and direction are not reported ("no volume data", log). A post-settlement trade has only 15:00 to 15:08, 8 minutes, before F. Nothing is documented to trade |
| X-10 K7-fomcvol-01 | An FOMC-hour or release-minute volatility member for MBT (K7-029 P-K7-029-a; K7-031 P-K7-031-a, P-K7-031-b; K7-030 P-K7-030-a) | D6 (family D gates not ported); rule 1 | The evidence covers mean absolute returns, jumps and spreads, not signed returns (P-K7-029-a "mean absolute hourly returns"). Family D state gates condition a base strategy and are not ported (D6). The FOMC and release clocks enter K7-ml-01 (KF1, KF2). K7-030's spread widening at release minutes is what D8's event-window cost and D9.5a already encode |
| X-11 K7-daysess-01 | Short MBT over the US day session, because bitcoin's gains accrue outside US hours (K7-027 P-K7-027-a; K7-039 P-K7-039-e; K7-040 P-K7-040-b) | D6 (family A clock drift not ported); rule 1 | The sources say day-session returns "diminished" (P-K7-040-b) and are "relatively small and volatile" (P-K7-039-e); none documents a negative day-session mean. It is a drift bet on the clock, which D6 does not port, because on a product without a documented drift it measures the window's trend |
| X-12 K7-ethlead-01 | Trade MBT on a lagged MET or ether move (inside K7; MET as a signal leg) | Rule 1; D1/D9 coverage | The only lead-lag passage runs the other way: "BTC leads ETH price adjustment" (P-K7-021-b). ETH jumps are more news-sensitive, but "co-jumps among Bitcoin and Ethereum are scarce" (P-K7-031-a, P-K7-031-c). MET's day-session coverage is 0.947 < 0.95 (D1), so the leg would likely fail D9's check. CME's ETH/BTC relative-value pieces are daily and trade MET (R-K7-063) |
| X-13 K7-fda-01 | Forecast the next day's intraday return curve by functional data analysis; buy at the forecast minimum and sell at the forecast maximum (K7-017 P-K7-017-a, P-K7-017-b, P-K7-017-c) | Rule 1; D15.2 | The curves are 24-hour Bitstamp curves, and a CME-session redefinition with an exit by F is untested (log). The result flips sign with the training length: "a positive Sharpe ratio if S = 182, while a negative Sharpe ratio if S = 365" (P-K7-017-e). A rolling re-estimated forecast model is a flexible-model search, and the cluster's one flexible model is K7-ml-01 |
| X-14 K7-fri-01 | Long bitcoin from Friday 3 p.m. EST (14:00 CT) for 4 to 24 hours (K7-015 P-K7-015-b, P-K7-015-c) | Not intraday-feasible | The hold crosses Friday's 15:08 CT flatten and the weekend (TopstepX "closed till Sunday at 5:00 PM", F4). The one-hour Friday variant is the paper's benchmark ("only investing from 3:00:00 p.m. to 3:59:59 p.m. on Fridays"), which its strategies outperform (P-K7-015-c); it is not a hypothesis. Only a few hourly means are significant (P-K7-015-d) |
| X-15 K7-preholiday-01 | Buy bitcoin at the close before a US holiday and sell at the close after (K7-041 P-K7-041-b, P-K7-041-c) | Not intraday-feasible | Close-to-close holds through the holiday and nights. A same-day pre-holiday session variant has no passage |
| X-16 K7-utc2100-01 | Long 21:00-23:00 UTC (K7-039 P-K7-039-c), or overnight after NYSE close at a 10-day high (K7-040 P-K7-040-e) | Not intraday-feasible | 21:00-23:00 UTC is 15:00-17:00 CT in winter and 16:00-18:00 CT in summer: after F, and across CME's daily break before 2026-05-29. K7-040's rule holds overnight |
| X-17 K7-hftlead-01 | Trade MBT's sub-second lead over spot (K7-025 P-K7-025-b, P-K7-025-c; K7-003 P-K7-003-b) | D9.3; D9.4 | The lead is 0.055 to 0.15 seconds. Any rule on it is the "average durations measured in seconds" pattern [F7.3] and needs latency the program does not model |
| X-18 K7-mlprec-01 | A second learned model: LSTM classification at 15-minute or hourly bars (K7-028 P-K7-028-a, P-K7-028-b), or LASSO-BMA predictor selection (K7-016 P-K7-016-a, P-K7-016-b) | D15.2 | One ML member per cluster (D15). Their horizons for a same-day trade are [unverified] (log). They are precedents for K7-ml-01 only |

---

## 3. Beyond budget (lead decides)

None. The log supports 3 new members inside the budget of 11 non-port, non-ML slots. The following
were considered and not written; none is a budget overflow:
- **A day-session variant of K7-expiry-01,** entering at 08:30 CT instead of T_exp - 300 min.
  - What it would do: survive a failed overnight coverage check (C12).
  - Why not written: it is a different window from the documented one, P-K7-005-b's 5 hours. It would
    be one more trial. The lead may add it now as a declared fallback, but not after the coverage
    result is seen.
- **1-hour and 4-hour versions of K7-rev2h-01** (P-K7-012-b: -0.0557 and -0.0564). Not written: the
  source's headline and strongest horizon is 2 hours. Each would be one more trial.
- **A Friday BFF / BRRNY-window member** (P-K7-038-b). No direction is documented (X-08).
- **A post-expiry member.** K7-005's pooled robustness says "No effects are detected after then"
  (P-K7-005-d). Nothing to write.

---

## 4. Routed to K8

These are the K7 reader's flags (log section 4). K8's dispositions are copied from
reports/stage_e0_research_K8.md rows F35 to F46 for the record. None was read by this writer.

| Source | Legs | One phrase | K8 disposition (K8 log) |
|---|---|---|---|
| Conlon, Corbet, Oxley (2024), JFM 10.1002/fut.22541 | VIX-family (K1) and CME bitcoin basis (K7) | equity-volatility sentiment and bitcoin basis | F35: sentiment, shelved |
| Kose et al. (2024), JFM 10.1002/fut.22487 | VIX, dollar, gold, oil (K1, K3, K5, K4) and bitcoin (K7) | global drivers of the bitcoin price | F36: rejected (daily and weekly SVAR) |
| Aalborg et al. (2018), SSRN 3233977 | VIX (K1) and bitcoin (K7) | daily drivers | F37: rejected (daily drivers) |
| Mourey et al. (2025), SSRN 5382090 (registry K8-004, tagged K7 and K1) | weekend crypto returns (K7 signal) and Monday equity indices (K1) | weekend crypto move as a Monday equity signal | F38: passed by K8 (abstract only). Note for K8: since 2026-05-29 the weekend crypto move is also visible in CME's own MBT bars, but those bars belong to no program trade date (C3), and TopstepX stays closed at weekends (F4) |
| arXiv 2505.14655, (Micro)Strategy and bitcoin | bitcoin (K7) and single stocks | crypto-equity link | F39: rejected |
| Krause (2026) SSRN 6925619; Lee (2024) SSRN 5033066 | bitcoin (K7) and equity indices (K1) | ETF-era correlation change | F40: rejected |
| Shakourloo (2026), SSRN 6377464 | bitcoin (K7) and macro variables | lead-lag | F41: rejected |
| Joo (2023), SSRN 4355765 | bitcoin (K7) and HG, NG, GC, CL (K5, K4) | hedge ratios | F42: rejected |
| Mazur (2024), SSRN 4810965 (K7-027), gold-ETF item P-K7-027-c | bitcoin-ETF inflows (K7) and gold-ETF outflows (K5) | flow substitution | F43: duplicate of K7-027 |
| CME economic research, bitcoin with equities and gold (2025, 2026) | bitcoin (K7), equities (K1), gold (K5) | correlation regime commentary | F44: rejected |
| Pinchuk (K7-026), 5-year note futures as a control | bitcoin (K7), rates (K2) | rates only as a control | F45: duplicate of K7-026 |
| Quantpedia bitcoin-and-gold / equities items (five titles) | bitcoin (K7), gold (K5), equities (K1) | allocation and ETF-spread ideas | F46: rejected |

This catalog adds no new K8 routing.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K7.md section 3 (K7-001 to K7-043, of
which K7-035 is a blocked stub). No `[K7]`-tagged passage exists in any other log.

| Item | Disposition |
|---|---|
| K7-001 Baur, Dimpfl (spot leads futures; abstract only) | Excluded as a member, X-02. Evidence only |
| K7-002 Alexander, Heck (CME absorbs shocks in 4-5 minutes, 2019-2020) | Excluded as a member, X-02. Used as transfer reasoning in K7-expiry-01 and K7-rev2h-01 (P-b). Used for clock facts in C3 (P-e). P-f (saw-tooth near monthly expiry) is context for C8's roll reasoning |
| K7-003 Frino et al. (futures generally lead; specification-sensitive) | Evidence against X-02 and in X-17 (P-a, P-b). Used in K7-ml-01 KF1 (P-c). The Tether-tweet part is social media, shelved |
| K7-004 Quantpedia, expiry-event daily study | Conflicting evidence stated in K7-expiry-01 (P-b, P-c). Its d+1 and d+2 legs cross the weekend: not intraday-feasible. P-d's time is superseded by K7-033's primary text |
| K7-005 Blasco, Corredor, Satrústegui (pre-expiry spot returns) | **Used:** K7-expiry-01 (P-a, b, c, d, e, f); K7-ml-01 KF3 |
| K7-006 Robertson, Zhang (CME leads) | Evidence against X-02 (P-b) |
| K7-007 Ngene, Wang (basis-conditioned 5-minute feedback) | Excluded, X-06 (insufficient evidence: no traceable parameters) |
| K7-008 Hattori, Ishida (crash arbitrage, CBOE) | Excluded, X-06 (not intraday-feasible: two legs to expiry) |
| K7-009 Pati (MBT informativeness, intraday) | Insufficient evidence: blocked, title only. The only MBT-specific item; an open lead (section 7, item 12) |
| K7-010 Baur, Cahill, Godfrey, Liu (time-of-day effects; "no consistent or persistent patterns") | Insufficient evidence for a member. It is negative evidence for family A/E clock effects (P-b); D6 does not port family A |
| K7-011 Shen, Urquhart, Wang (first half hour predicts last) | **Covered by CP1.** The paper's own target window (to 16:00 CT) is not intraday-feasible under F. P-f's anti-persistence is cited in K7-rev2h-01. Used in K7-ml-01 KF7 (P-b, P-c) |
| K7-012 De Nicola (1-4 hour negative autocorrelation) | **Used:** K7-rev2h-01 (P-a, b, c, e, f); K7-ml-01 KF5, KF6. Conflicting evidence stated in K7-montrend-01 |
| K7-013 Eross et al. (n-shaped volume, spread, volatility) | Insufficient evidence for a directional member (stylized facts). Used as reasoning for K7-ml-01's day-session window (P-a) |
| K7-014 Lee et al. (post-ETF volatility spike 08:30-09:00 CT) | Insufficient evidence for a directional member (volatility and tails; the median is unaffected, P-b). Used in K7-ml-01 KF7 and window placement; context for CP2's opening range |
| K7-015 Miralles-Quirós (Friday 3 p.m.) | Excluded, X-14 (not intraday-feasible). Used in K7-ml-01 KF4 (P-b) |
| K7-016 Huang, Gao (LASSO-BMA) | Excluded, X-18 |
| K7-017 Bouri et al. (functional return curves) | Excluded, X-13 |
| K7-018 Wen, Bouri, Xu, Zhao (momentum and reversal; FOMC days) | Momentum part **covered by CP1**. FOMC conditioning used in K7-ml-01 KF2 (P-a). Reversal part: insufficient evidence (segment definitions unverified); cited as conflicting evidence in K7-rev2h-01 |
| K7-019 CF Benchmarks methodology v17.4 | **Used:** K7-expiry-01 (P-a, P-b, P-d); K7-ml-01 KF3. BRRNY part excluded, X-08 (P-c) |
| K7-020 Lim (ETF flows) | Excluded, X-03 |
| K7-021 Aleti, Mizrach (CME leads; BTC leads ETH) | Evidence against X-02 (P-b). Excluded as a MET-signal member, X-12; the reason MET is not read by K7-ml-01 |
| K7-022 Deprez, Frömmel (75,360 technical rules) | **Covered by CP2** (the breakout family), with a negative prior. Conflicting evidence for K7-rev2h-01 |
| K7-023 Wątorek et al. (release-time bursts; 12:30 UTC component) | Excluded as a member, X-05. Used in K7-ml-01 KF1 |
| K7-024 Chi, Chu, Hao (on-chain flows) | Excluded, X-07 (rule 3). Cited for K7-ml-01's h (P-a) |
| K7-025 Plazuelo Pascual et al. (MBT leads Binance, sub-second) | Excluded, X-17. Used as transfer reasoning in K7-expiry-01 and K7-rev2h-01 (P-b). Evidence against X-02 |
| K7-026 Pinchuk (bitcoin falls on inflation surprises) | Excluded as a member, X-04. Used in K7-ml-01 KF1. Rates-control part routed to K8 (section 4) |
| K7-027 Mazur (spot ETF facts) | Excluded, X-03 and X-11. Gold-ETF item routed to K8 |
| K7-028 Kryńska, Ślepaczuk (LSTM) | Excluded, X-18 |
| K7-029 Yang, Wang (FOMC volatility and volume) | Excluded as a member, X-10. Used in K7-ml-01 KF2 and the h choice |
| K7-030 Mercik, Będowska-Sójka (spreads at release minutes) | Excluded as a member, X-10 (a cost state, which D8 and D9.5a already encode) |
| K7-031 Ben Omrane et al. (macro news and BTC/ETH jumps) | Excluded as a member, X-10 and X-12. Used in K7-ml-01 KF1 |
| K7-032 CME, Analysis of the BRR | **Used:** K7-expiry-01 (P-a, P-b; the BRR window). P-e is background for X-08 |
| K7-033 CME, MBT FAQ | **Used:** C3 (P-b), C9 EC-MBTX (P-c, P-d), C13 (P-e), CP1 and CP3 (P-a), K7-expiry-01, K7-ml-01 KF3. The settlement-minute mechanism is excluded, X-09 |
| K7-034 CME, BTIC on crypto futures | Excluded as a member, X-08 (no direction). P-d (no BTIC on the last trade date) is noted, not used |
| K7-035 CME Bitcoin Futures Liquidity Report | Blocked (stub). Nothing |
| K7-036 CME, 24/7 trading article | Excluded as a member, X-01 (the brief's reason). **Its 29 May 2026 date is now verified** by CME's own releases (preamble). Header and C3 |
| K7-037 CME, TAS FAQ | Excluded, X-09 |
| K7-038 CME, Bitcoin Friday futures (BRRNY) | Excluded as a member, X-08. Used in K7-ml-01 KF4 (P-b); context for CP1 (P-a) |
| K7-039 Padyšák, Vojtko (21:00-23:00 UTC) | Excluded, X-16 (not intraday-feasible). Evidence in X-11 |
| K7-040 Dujava (overnight sessions) | Excluded, X-16 (not intraday-feasible). Evidence in X-11. Used in K7-ml-01 KF4 (P-c) |
| K7-041 Dujava (pre-holiday) | Excluded, X-15 (not intraday-feasible) |
| K7-042 Pagani (Concretum, Sunday-evening trend) | **Used:** K7-montrend-01 (P-a, b, c, d, e); K7-ml-01 KF4, KF5. Conflicting evidence for K7-rev2h-01 |
| K7-043 Quant Fiction (month-of-year, max-statistic permutation) | Not intraday-feasible (monthly) and negative. Its max-statistic permutation design is a methodological note for the lead's multiple-comparisons work; no member |
| `[K7]` passages in the K1 to K6 and K8 logs | None. The K8 log's F35 to F46 are dispositions of K7's flags (section 4). Registry line K8-004 (tagged K7) is K8's claim |
| R-K7-019 Howard (2026), SSRN 7067778 | Not passed by the reader. A possible panel of eight CME futures with MBO order-book data, left unclaimed for the lead; its seconds-horizon mechanism would fail D9.3/D9.4 anyway |
| R-K7-026 Su et al. (2022); R-K7-036 Kia, Song, Xu (2024) | Not passed (no abstract reachable); open leads for the lead. Not used |
| R-K7-001 to R-K7-073 (the rest) | Rejected at pre-filter or on reading. Not used |

**Correlated members, flagged for the lead's Tier-A accounting (not duplicates).**
- **K7-rev2h-01 and K7-montrend-01** bet opposite signs at related horizons: a 2-hour reversal in
  every day session, and a 1-hour trend in the Monday window. Their only overlap is Mondays 10:31-14:00
  CT, where both can hold positions.
- **CP1 and K7-ml-01's B2 and KF7** read the same overnight and first-half-hour moves.
- **K7-expiry-01 and K7-ml-01's KF3** use the same expiry clock.

---

## 6. Trial count table

| Member | Exposure | Grid points | Trials in N (bitcoin admitted by D2) |
|---|---|---|---|
| K7-cp1-01 | bitcoin | 1 | 1 |
| K7-cp2-01 | bitcoin | 1 | 1 |
| K7-cp3-01 | bitcoin | 1 | 1 |
| K7-expiry-01 | bitcoin | 1 | 1 |
| K7-rev2h-01 | bitcoin | 1 | 1 |
| K7-montrend-01 | bitcoin | 1 | 1 |
| ~~K7-ml-01~~ [excluded, U6] | bitcoin (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **7** = 3 port + 3 new + 1 ML. **0** if D2 does not admit bitcoin |

If the user re-admits MET (borderline at 0.947), ether would add 3 port trials. No new member here
is written for ether.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **24/7 CME crypto trading is confirmed.** CME's 1 June 2026 release says it "went live on Friday,
   May 29" (preamble). So:
   - X-01's exclusion holds, and the brief's "(K7-036, unverified)" can be upgraded.
   - D6's crypto session table, D10's equity-and-crypto calendar and E.2's bar builder need a crypto
     note for dates from 2026-05-29: bars now exist at weekends and at 16:00-16:59 CT on weekdays.
   - The lead decides the design wording.
2. **Trade-date convention after the change.**
   - CME now assigns weekend and holiday trading "a trade date of the following business day". This
     catalog keeps the program convention, [d-1 17:00, d 16:00) CT (C3).
   - Under that convention, Monday's first bar is Sunday 17:00 CT in both regimes, and no member reads
     weekend bars.
   - If the lead adopts CME's assignment, CP1's Monday signal and K7-ml-01's B2 on Mondays would start
     at Friday 16:00 CT and read weekend prices. That would change their meaning on the research
     window's last three Mondays and on every deployed Monday.
3. **Regime mismatch.**
   - The confirmation window (MBT's listing on 2021-05-03 to 2024-02-29) is entirely pre-24/7 and
     almost entirely pre-spot-ETF. Deployment would be post-both.
   - A K7 null or edge therefore describes the older regime. That matters most for the Monday members
     (CP1 on Mondays, K7-montrend-01) and for K7-expiry-01, whose only post-2021 evidence reverses
     sign (P-K7-004-b).
   - The lead may want NULL_CRITERIA_E's K7 statement to say this.
4. **Short history.**
   - MBT listed 2021-05-03, so its confirmation window has at most 739 weekdays. D4's start rule may
     shorten it further if MBT's 2021-2022 one-minute volume was below 0.25 x the 2025-26 reference.
   - D2 and D4 allow "the exposure's full-size contract bars" as a price path. For bitcoin that would
     be CME BTC (5 bitcoin, P-K7-005-a), which is not Topstep-permitted, not in the D1 table and not
     in D13's purchase plan.
   - Whether BTC bars may stand in is for the lead and the user.
5. **Coverage outside the day session (C12).**
   - K7-expiry-01 (from 05:00 or 06:00 CT) and K7-montrend-01 (Sunday 17:00 CT to Monday 14:00 CT)
     depend on MBT's overnight coverage, which D1 did not measure.
   - If they fail D9's check, they drop before screening. No fallback is written; a day-session expiry
     variant would be one more trial (section 3).
   - The lead may declare such a fallback now, before E.2 computes coverage.
6. **Low-frequency members.**
   - K7-expiry-01 trades about 12 research dates and needs about 25 x eps per event. K7-montrend-01
     trades about 55 Mondays and needs about 5.5 x eps per Monday (C11).
   - Both are likely "null at eps" or "inconclusive by design".
   - The 21:52 ruling on K4 (Q4) kept such members and let the power check decide. The lead may cut
     either (1 trial each).
7. **ML sample size.**
   - K7-ml-01 has about 1,100-1,200 research rows, fewer than D15.1's "few thousand". The monthly roll
     blackout alone removes about 45 dates.
   - Each of D15.5's six blocks holds about 190 rows. With min_data_in_leaf = 200, the early inner
     folds (2 to 3 blocks of training) can grow only one to three leaves.
   - D15 is common to all clusters, so this is flagged, not changed.
8. **Expiry days and the roll blackout.**
   - K7-expiry-01 trades only expiry days whose MBT.v.0 splice came on or before the Thursday of that
     week (C8). E.2 should report the count before screening.
   - If it is zero or near zero, the lead decides whether the member is withdrawn (logged) or whether
     the roll convention for MBT should differ.
9. **Cost sample.**
   - D8's five sample dates are Wednesdays, so the Sunday-evening buckets used by K7-montrend-01 are
     calibrated on Tuesday evenings. The 05:00-11:00 buckets of K7-expiry-01 are calibrated on
     ordinary Wednesdays, never on an expiry Friday.
   - Sunday-evening costs just after a pre-change CME reopen may be understated.
   - The lead decides whether to add a Monday trade date (with its Sunday evening) to MBT's mbp-1
     sample: a small spend, quoted in E.1.
10. **MET.** MET is out at 0.947, and no member reads it. If the user re-admits it:
    - ether gains the three ports (+3 trials);
    - the ML member could be re-written to read MET, but only with the coverage check passed.
11. **Rulebook chapter.**
    - The liquidity JSON gives MBT as "CME 348". The K7 log looked for "chapter 350/350A" (R-K7-061).
    - E.2 reads the correct chapter for MBT's price-fluctuation limits (C13) and for the expiry rule
      (checked against P-K7-033-c).
12. **Open leads (not researched here; no search tools):**
    - K7-009, Pati (2022), the only MBT-specific intraday study (blocked);
    - R-K7-026, Su et al. (2022);
    - R-K7-036, Kia, Song and Xu (2024), ETF price discovery;
    - R-K7-019, Howard (2026), a possible CME panel.
13. **E.2 checks named in this catalog:**
    - (a) EC-MBTX dates against CME's published MBT calendar, and T_exp by zoneinfo (C9).
    - (b) The standard 08:30 ET time of each CPI and PPI release in the BLS files (C9).
    - (c) MBT tick history, 2021-2026 (C7).
    - (d) MBT price-limit rules against Topstep's 2% rule (C13).
    - (e) Member-level coverage for [T_exp - 300, T_exp - 1] on expiry days, [Sunday 17:00, Monday
      14:00) on Mondays, the day session, and 09:31-14:30.
    - (f) The number of expiry days outside the roll blackout (item 8).
    - (g) D10 crypto entries after 2026-05-29, and the early-close status of 2025-11-28 and 2025-12-24.
    - (h) Whether D1's liquidity and coverage figures are affected by the regime change. They are not:
      the five calibration dates all predate it.

---

# Cluster K8

# Stage E.0 hypothesis catalog, cluster K8 (cross-cluster relationships)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K8-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K8 runs last.
> **K8 after the decisions: 3 active members, 4 confirmation trials** (3 new, no ports; K8-flight-01 2, K8-oilcad-01 1, K8-wkndbtc-01 1). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K8-OpusXHigh (Stage E.0 Task 4), 2026-09-24, about 02:00-02:45 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** No price, bar, tick or order-book data of any product was
opened, downloaded, charted or summarized, including the MES bars on disk. The only product-specific
numbers used are:
- contract specifications and public ADV (reports/stage_e0_liquidity.json; design D1 table);
- Topstep's published fees, hours, release table and risk rules (reports/stage_e0_topstep_facts.md
  F3, F4, F6, F12, as quoted in design D9);
- calendar metadata (dates and clock times only: the EIA WPSR schedule, FOMC, BLS, CME holidays), as
  the K3, K4, K5 and K7 catalogs specified and sourced them;
- MES's own confirmation start S = 2020-02-03 (Stage D.1f run: progress.md 2026-09-23 entry;
  docs/STAGES.md).

No price level, range, trend or volatility of any product is used or assumed below. Every threshold
is either a passage value or a judgment stated with its reason, and every rolling statistic is
computed by the harness from earlier bars at run time.

**Inputs read in full:**
- reports/stage_e0_research_K8.md (sections 0-5, with the routed-flag table F01-F47).
- `[K8]`-tagged passages in the other logs: **none exist.** `grep -n '\[K8\]'` over
  reports/stage_e0_research_K1.md to K7.md returns nothing. The "Flags for K8" sections were read:
  K1 lines 524-528, K2 434-439, K3 631-637, K4 691-704, K5 561-573, K6 692-702, K7 744-757. All of
  them are in the K8 log's F table.
- reports/stage_e0_source_registry.jsonl: K8-001 to K8-008 (lines 271-278). No other line is
  tagged K8.
- docs/STAGE_E_DESIGN.md D1-D15, with the 21:12 and 21:52 amendments and the D9 rulings of 01:40 and
  01:52.
- docs/NULL_CRITERIA_E.md, including section 3 (the "source-overlap" label) and section 8
  (cross-cluster members).
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md: F3 fees, F4 hours, F6 releases.
- reports/stage_e0_liquidity.json: the NQ, MNQ, MBT, CL, MCL, 6C, GC and MGC rows.
- reports/stage_e0_catalog_K2.md to K7.md, for duplicates and format and for their "Routed to K8"
  sections. The K1 catalog did not exist when this was written.
- data/research_bars.py and data/build_mes_bars.py: docstrings and constants only, to confirm
  that the owned MES build spans the Globex session (daily halt 16:00-17:00 CT) and which date
  classes its loaders serve. No bar was loaded.

**Checks in the K8 reader's saved copies.** Two checks were made in
scratchpad/fetch/alquist.txt and scratchpad/fetch/zdg.txt. They only read the definitions of numbers
already logged; no mechanism was taken from them.
- **Alquist, Ellwanger, Jin, eq. (4) and Tables 4-5.** The "marginal effects" are coefficients of
  an asset's event-window return on the oil-futures return.
  - P-K8-001-f's CAD value of 0.090 is therefore a return-on-return coefficient.
  - The same table family's equity figure, 0.110 after 2008M9, is the logged "1.1% increase" per
    10% oil (P-K8-001-c).
  - A positive exchange-rate effect is a dollar depreciation (P-K8-001-e). That is a rise in the
    USD price of the foreign currency, the direction in which 6C rises.
- **Zhang, Dufour, Galbraith, Table 1 note** (the same note as P-K8-006-e): "The daily CAD/USD,
  CAD/GBP and CERI are from Statistics Canada. The WTI crude oil price and Brent crude oil price are
  from Energy Information Administration." It is used in X-05.
- The scratchpad files named baur.pdf and baur2.pdf are "Content Blocked" HTML pages, not the paper.
  K8-003 stays abstract-only.

**Official pages fetched in this task:** none. The calendar and session facts are the ones other
CatalogWriters fetched and quoted:
- EC-WPSR: K4 catalog C9;
- EC-FOMC and EC-BLS: K5 catalog C9;
- CME's 24/7 crypto trading from 2026-05-29: K7 catalog preamble and C3.

---

## 0. Header

| Item | Value |
|---|---|
| Cluster | K8, cross-cluster relationships. Each member has a signal leg in one of K1-K7 and a traded leg in another (partition section 3) |
| Members | **4 = 3 new + 1 ML member. No core ports in K8** (K8 has no products of its own; the ports live in K1-K7). The budget is 15, so 11 slots are unused. The log is thin: 7 items passed, of which 3 are abstract-only and 2 carry no direction. Nothing is padded (section 3) |
| Trials in N (confirmation) | **5 if D2 admits gold, CAD and the Nasdaq-100.** K8-flight-01 2 (exit grid), K8-oilcad-01 1, K8-wkndbtc-01 1, ~~K8-ml-01 1~~ [U6: excluded; K8 has 4 trials]. In general 2a_G + 2a_C + a_N, where each a is 1 if D2 admits that exposure |
| ML grid | ~~48 configurations, counted only in the K8 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Traded legs used | gold {GC, MGC\*} (K5); CAD {6C} (K3); Nasdaq-100 {MNQ\*, NQ} (K1). Each is traded only if D2 admits the exposure. The vehicle is "D2 (chosen in E.2)" throughout |
| Signal legs used | S&P 500 on MES bars (K1; a leg only, D1.5; owned, non-holdout dates). WTI crude on the crude exposure's price-path series (K4). Bitcoin on MBT bars (K7). No member reads NKD, 6M or MET |
| Statement unit | NULL_CRITERIA_E section 8. Each member is stated under K8 only. Its eps is the traded leg's exposure's eps_X, and it enters K8's own Holm family (D5). Its window is the intersection of its legs' windows (D4) |
| Source overlap | **K8-wkndbtc-01 is labelled "source-overlap"**; no other member is (C15) |
| Starred contracts | MGC\* and MNQ\* can be vehicles (D9.8; referent F12.1, encoded as D9.11 and D9.12). GC, 6C and NQ are unstarred |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event
  (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values are usable
  from then on. C_X(tau) is the close of leg X's bar at tau.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open, the engine convention
  of D6 and D15. "Market intent on the bar at X" fills at the open of the bar at X + 1 min. The ML
  member follows D15.3 (decision at t_j, fill at the open of the bar at t_j + 1 min).
- **C3 Trade date and hours.**
  - **Trade date:** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). The first bar of a
    Monday trade date is the Sunday 17:00 CT bar.
  - **Topstep hours** (F4): "Sunday open | 5:00 PM CT", "Weekday reopen | 5:00 PM CT", "All
    positions must be closed by 3:10 PM CT every weekday".
  - **MBT, two regimes.** Before 2026-05-29, CME's crypto session had a daily 16:00-17:00 CT break
    and a weekend closure from Friday 16:00 to Sunday 17:00 CT. From 2026-05-29 16:00 CT it trades
    continuously (K7 catalog preamble and C3, quoting CME's releases of 19 Feb and 1 June 2026).
  - **Program convention kept.** Following the K7 catalog's C3, no K8 rule reads a bar outside a
    program trade date.
- **C4 Cross-leg synchronization (rule 3; D11.5).** Every leg is a set of CME Globex ohlcv-1m bars on
  one UTC minute grid.
  - At decision time t, a signal reads only bars of its own leg whose close is at or before t, that
    is the bar at t - 1 and earlier.
  - The traded leg's intent is emitted on the traded leg's own bar at t - 1 and fills at the open of
    its bar at t (C2). No signal value comes from a bar that closes after the fill.
  - No forward fill. A missing signal bar, or a change of instrument_id between the bars of one
    computation, means no trade at t.
  - Signals are percent returns or signs, so they give the same decision on any contract of the
    signal leg's exposure.
- **C5 Exclusions for the three new members.**
  - A member does not trade on:
    - the traded leg's roll-blackout dates (`screen_candidate` with `roll_blackout`: the splice trade
      date plus the 2 sessions before it);
    - dates that any leg's D10 group calendar (equity-and-crypto, energy, FX, metals) marks as early
      close, early halt or closure;
    - dates on which a bar the rule reads, or the entry bar, is missing.
  - If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
    flatten at F is the backstop.
  - **Signal-leg rolls.** Signal-leg roll-blackout dates are not excluded. A signal leg's bars come
    from its exposure's volume-ranked continuous series, and every computation requires one
    instrument_id (C4; question 3).
  - **Warm-up.** A rolling multi-day statistic uses only earlier trade dates of the same window
    (research or confirmation) that pass these exclusions. The first 20 such dates of each window are
    warm-up and carry no trade.
  - Nothing is ever read from embargo, holdout-2 or holdout-1 dates.
- **C6 Guarded entries.** An entry whose fill would land in a D9.5a guarded interval [release,
  release + 2 min) of the traded product is **skipped, not deferred.** Every K8 entry signal is
  measured on bars before its decision time, so a fill deferred past a release would act on a signal
  the release has just made stale. This is stricter than D9.5a's default deferral (question 6).
  Exits deferred by D9.5a are left to the harness; they only lengthen a hold.

  The releases that concern each traded product (D8: Topstep F6.4 plus the releases the product's
  catalog members name) are:

  | Traded exposure | Releases (CT) | Basis |
  |---|---|---|
  | gold | Employment Situation 07:30; CPI 07:30; FOMC statement 13:00 (LBMA auction starts: D8 cost only, pending the lead) | K5 catalog C11 |
  | CAD (6C) | Employment Situation 07:30; FOMC statement 13:00; EIA WPSR at T_W(d) | F6.4 ("Unemployment Rate / 7:30 AM" lists 6C; "FOMC Statement / 1:00 PM / All products"). WPSR is named by K8-ml-01 (KF3, KF4) and is the signal leg's release in K8-oilcad-01 (question 5) |
  | Nasdaq-100 | Employment Situation 07:30; CPI 07:30; FOMC statement 13:00 | F6.4; D9.12 |

- **C7 Size.** Each member trades q_c of its traded leg's D2 vehicle, never above 1 lot-equivalent
  (D2, D9.5). A signal leg takes no position and has lot-equivalent 0. Each member's total position
  is therefore its traded leg's, and no two-leg position exists in this catalog (rule 5). No member
  sizes by signal.
- **C8 Ticks and fees.** Ticks are from reports/stage_e0_liquidity.json (CME contract specifications,
  fetched 2026-09-23 20:41-20:51 PDT). Round turns are Topstep F3.

  | Contract | Role | Exposure (cluster) | Tick | Tick value | Topstep round turn | Round turn in ticks | Lot-equivalent |
  |---|---|---|---|---|---|---|---|
  | GC | traded | gold (K5) | 0.10 | $10.00 | $4.32 | 0.43 | 1 |
  | MGC\* | traded | gold (K5) | 0.10 | $1.00 | $1.92 | 1.92 | 0.1 |
  | 6C | traded | CAD (K3) | 0.00005 | $5.00 | $4.22 | 0.84 | 1 |
  | NQ | traded | Nasdaq-100 (K1) | 0.25 | $5.00 | $3.78 | 0.76 | 1 |
  | MNQ\* | traded | Nasdaq-100 (K1) | 0.25 | $0.50 | $1.22 | 2.44 | 0.1 |
  | MES | signal only | S&P 500 (K1) | 0.25 | $1.25 | n/a | n/a | 0 (no position) |
  | CL, QM, MCL | signal only | crude (K4) | 0.01, 0.025, 0.01 | n/a | n/a | n/a | 0 (no position) |
  | MBT | signal only | bitcoin (K7) | $5.00 per bitcoin | $0.50 | n/a | n/a | 0 (no position) |

  Within the gold and Nasdaq-100 exposures, both contracts have the same tick in price units. No K8
  rule is in ticks; the ML member's B-features are in ticks of 6C, the only CAD contract. E.2
  confirms that the ticks were unchanged over 2019-05..2026-06.
- **C9 Price data.**
  - **MES (signal leg, owned).**
    - The research parquet is `ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet`. The
      confirmation bars cover 2019-05-01..2024-02-29.
    - Both are served by data/research_bars.py, whose loaders refuse holdout, embargo and
      wrong-class dates.
    - The build spans the Globex session with the daily 16:00-17:00 CT halt.
    - MES's own start rule gave S = 2020-02-03 (D.1f), so every MES leg's confirmation window starts
      no earlier than 2020-02-03.
    - Holdout-2 (2024-03..2025-03) and holdout-1 (from 2026-06-22) stay sealed. No K8 member reads
      them.
  - **Traded vehicles, crude and MBT.** Databento GLBX.MDP3 ohlcv-1m, paid. The research window is
    bought in E.1; the confirmation and holdout-2 history of the chosen vehicle is bought in E.2b
    (D13).
  - **History** (liquidity JSON listing dates; D13's pre-listing quote failures):
    - GC, NQ, 6C, CL and QM: 2019-05 onward;
    - MGC: listed 2010-10-04;
    - MNQ: listed 2019-05-06;
    - MCL: listed 2021-07-12;
    - **MBT: listed 2021-05-03, so it has no bars for 2019-05..2021-04.**
  - **The crude signal series.** D13 buys one chosen vehicle per exposure. The crude leg reads the
    crude exposure's price-path bars as E.2 declares them under D2 and D4: CL's bars if CL is the
    vehicle or is declared MCL's price path, otherwise the vehicle's own bars. The rules use percent
    returns, so they are the same on any crude contract.
  - **Availability.** Every bar is available at its close (C1).
  - **mbp-1** enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C10 Event calendars.** All are external, free, and known before the trade date. No rule reads a
  released value.
  - **EC-WPSR (EIA Weekly Petroleum Status Report)**, exactly as the K4 catalog's C9 specifies it:
    - standard slot "10:30 a.m. eastern time on Wednesdays", which is 09:30 CT;
    - exceptions from EIA's yearly tables, for example Thursday 11:00 ET in 2019, Thursday 12:00 ET
      in 2025-2026, and 2025-12-29 Monday 5:00 p.m. ET;
    - sources: the EIA schedule page and one Wayback capture per year, 2019-2026;
    - T_W(d) is the scheduled release time in CT on d, from the schedule known the evening before d.
      The D8 cost and the D9.5a guard use the actual time.
  - **EC-FOMC and EC-BLS**, exactly as the K5 catalog's C9: FOMC statement at 13:00 CT; Employment
    Situation and CPI at 07:30 CT.
  - **EC-CAL**: the D10 group calendars (equity-and-crypto, energy, FX, metals), which E.2 builds from
    CME's published schedules.
- **C11 Frequency (arithmetic from calendar counts; no price data).**
  - **Research window** 2025-04-01..2026-06-19:
    - 319 weekdays, about 305 CME trade dates (K4 catalog C11);
    - 63 Mondays, 5 of them US holiday Mondays with an equity early halt (2025-05-26, 2025-09-01,
      2026-01-19, 2026-02-16, 2026-05-25);
    - about 56 standard WPSR Wednesdays (K4 C11);
    - 10 FOMC statement days (K5 C12);
    - 20 warm-up dates per rolling member (C5).
  - **Confirmation window by earliest leg start:**
    - from 2019-05-06: 1,259 weekdays to 2024-02-29;
    - from 2020-02-03 (MES): 1,064 weekdays;
    - from 2021-05-03 (MBT): 739 weekdays, 148 Mondays.
    - All are before exclusions and before each leg's own start rule.
  - **Consequence (D5):** a member trading on k of about 305 research dates, with zeros on the rest,
    needs a net P&L per event of about (305 / k) x eps_X.
- **C12 Price-limit proximity (D9.7), per traded leg.**
  - **Nasdaq-100:** CME equity-index limits (7% overnight, per the Topstep page quoted in D9.7). They
    bite on K8-wkndbtc-01's Sunday-evening entries.
  - **Gold:** as the K5 catalog's C13. Whether a daily limit or a dynamic band applied is not
    verified in E.0; E.2 decides.
  - **6C:** as the K3 catalog's C11. No FX limit is established in E.0; E.2 decides.
  - The harness rule applies wherever a limit exists: no entry, and an immediate exit, beyond the stop
    level.
- **C13 Coverage.**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  - **Traded vehicle:** D9's member-level check (ohlcv-1m coverage of at least 0.95 in the member's
    own window, on the research window), with each member's window listed in its entry.
  - **Signal leg (K8 addition, proposed; question 4):** E.2 reports, on the research window, the share
    of the member's decision times at which every signal bar it needs is present. A member below
    0.95 is excluded before screening, with the reason logged. This matters most for K8-wkndbtc-01's
    two MBT minutes and for the crude bars before 08:00 CT that K8-ml-01 reads.
- **C14 Cost and statistics.**
  - **Cost:** each member pays its traded leg's D8 cost: Topstep's round turn plus the calibrated
    half-spread per 30-minute bucket, at q_c. A fill in [release, release + 30 min) after a C6
    release pays the event-window cost. Signal legs cost nothing.
  - **Daily series:** net P&L per contract of the traded vehicle, zeros on no-trade dates
    (NULL_CRITERIA_E section 3).
  - **eps:** the traded exposure's eps_X (section 8).
- **C15 Source overlap (NULL_CRITERIA_E section 3).** Each entry records its sources' sample windows
  against its confirmation window. That window ends on 2024-02-29 and starts no earlier than
  2019-05-06.

---

## 1. Members

### K8-flight-01 (flight to gold: long gold after an extreme negative 5-minute S&P 500 move)
- **Cluster** K8.
  - **Signal leg:** the S&P 500 exposure (K1), read on MES bars (C9; a leg only, D1.5).
  - **Traded leg:** gold (K5). Admissible contracts: GC and MGC\* (D1 table).
  - **Vehicle:** D2 (chosen in E.2). Traded only if D2 admits gold.
- **Mechanism:** after an extreme negative 5-minute S&P 500 move, gold rises. The passages:
  "extreme negative 5-min S&P500 returns lead to a positive reaction of the gold price" and "on days
  with extreme price declines in the stock market, gold continues to increase post US stock trading
  hours" (P-K8-003-b); "a fast reaction of gold prices to extreme negative stock returns consistent
  with a flight to gold" (P-K8-003-c). New to the program.
  - **Evidence status:** abstract only (K8-003). The following are [unverified]: the definition of
    "extreme", the lag, the response size, whether the gold series is spot or COMEX futures, and
    costs.
  - **Limits:**
    - A "fast" reaction may sit largely inside the same 5-minute interval as the equity move, which a
      next-open fill cannot capture. The member tests the part that follows the interval.
    - The post-close continuation lies after F (X-09). Only its in-session lead-in is tested (grid
      point HEOD).
- **Signal (on MES, K1 clock):**
  - **Blocks:** B_k = [08:30 + 5(k-1), 08:30 + 5k) CT for k = 1..77; the last is [14:50, 14:55).
    The decision time is t_k = 08:30 + 5k, from 08:35 to 14:55.
  - **Block return:** r_k = (C_MES(t_k - 1) - C_MES(t_k - 6)) / C_MES(t_k - 6), the move from the
    price at the block's start to the price at its end. Both bars must be present with one
    instrument_id; otherwise r_k is undefined and there is no trigger at t_k.
  - **Threshold Q(d):**
    - Collect every defined r_k (k = 1..77) on the 20 most recent earlier eligible dates of the same
      window (C5). Let n be their count.
    - n >= 1,200 is required (the maximum is 1,540); otherwise there is no trade on d.
    - Q(d) = the m-th smallest value, m = ceil(0.005 n); m = 8 when n = 1,540.
    - Q(d) is fixed before d's 08:30.
  - **Trigger at t_k:** r_k <= Q(d) and r_k < 0.
- **Entry rule:** at the first trigger of trade date d, BUY q_c: market intent on the gold vehicle's
  bar at t_k - 1, filling at the open of its bar at t_k. At most one entry per trade date. C6
  applies: on FOMC days a trigger at 13:00 (fill at 13:00) is skipped, and the member keeps watching
  later blocks.
- **Exit rule (grid, two points):**
  - **H30:** market intent on the gold bar at T_e + 29, where T_e is the entry fill minute, filling
    at the open of T_e + 30; or the HEOD exit, if that comes first.
  - **HEOD:** market intent on the gold bar at 15:04, filling at the 15:05 open.
- **Holding horizon:**
  - H30: 30 minutes for entries at or before 14:35, falling to 10 minutes for an entry at 14:55.
  - HEOD: from 10 minutes (entry at 14:55) to 6 h 30 min (entry at 08:35).
  - **Session window:** 08:35-15:05 CT. **Flat by F:** gold's F is 15:08 (D6 metals row); the last
    fill is at 15:05.
- **Data fields read:**
  - **MES ohlcv-1m close and instrument_id**, bars 08:29..14:54 CT. Owned (C9): on disk for
    2019-05-01..2024-02-29 and 2025-04-01..2026-06-19. Used from 2020-02-03 (MES's S). Available at
    each bar's close.
  - **Gold vehicle ohlcv-1m open and instrument_id**, 08:35..15:05 CT. Databento GLBX.MDP3, paid;
    history 2019-05..2026-06 (C9). Available at each bar's close.
  - **EC-CAL** (equity-and-crypto and metals groups), and **EC-FOMC and EC-BLS** (for C6 only).
    Free, known in advance.
- **Order type:** market. **Sizing:** q_c of the gold vehicle (GC: q = 1; MGC: q <= 10). The MES leg
  takes no position.
- **Parameters:**
  - **5-minute blocks:** the source's return interval ("extreme negative 5-min S&P500 returns",
    P-K8-003-b).
  - **Block clock 08:30-14:55 CT:** the US stock trading hours that the source contrasts with "post
    US stock trading hours" (P-K8-003-b). The cash session is 08:30-15:00 CT (D1's equity window).
    The last block ends at 14:55 so that every hold is at least 10 minutes.
  - **Tail at 0.5% of the trailing 20-date distribution (judgment).**
    - "Extreme" is not defined in the logged text.
    - A one-in-200 five-minute move is a tail event on any usual reading.
    - With 77 blocks a day, an unclustered 0.5% tail gives about 0.39 triggers a day. That leaves
      events for the power check (arithmetic from the definition, not a data estimate).
    - A trailing distribution measures "extreme" against the current volatility regime rather than a
      fixed level.
  - **20 trailing dates (judgment):** the lookback of D15's B4 feature. About 1,540 blocks, so the
    0.5% cut rests on about 8 order statistics.
  - **n >= 1,200 (judgment):** about 78% of the maximum, so a date with sparse history does not set
    its threshold from few blocks.
  - **One entry per trade date (judgment):** the claim concerns an event, and a day's first extreme
    block is that event.
  - **H30 (judgment):** stands for the "fast reaction" (P-K8-003-c); it is six of the source's
    5-minute intervals after the trigger.
  - **HEOD:** stands for the second claim, that gold "continues to increase" on extreme-decline days
    (P-K8-003-b). It holds to the last fill the XFA allows, with a 3-minute margin before F.
  - **Grid:** {H30, HEOD}, 2 points, each a trial.
- **Expected entries and holding:**
  - At most 1 entry per trade date.
  - Trigger days will be fewer than the unclustered 0.39 a day, because large equity moves cluster on
    volatile days. E.2 reports the count on the research window before screening.
  - Holds: 10-30 minutes (H30); 10 minutes to 6.5 hours (HEOD).
  - **Floor:** at most 1 entry a day (limit 20); every hold at least 10 minutes (so at least 2 full
    minutes); mean at least 10 minutes by construction. OK.
- **Falsification:**
  - **The standard condition:** UCB95 of the member's mean net daily P&L per contract of the gold
    vehicle below gold's eps_X, at >= 80% achieved null power on the intersected confirmation window,
    counts against it.
  - **Sign check (reported, not a trial):** the mean over trades of (gold open at exit - gold open at
    entry), in ticks, is positive.
  - **Clock control (descriptive):** the same gold interval (the entry minute to the exit minute) on
    the window's non-trigger dates. It separates a time-of-day drift in gold from the trigger's
    effect.
- **Topstep check (traded leg: gold):**
  1. **Flat by F:** last fill 15:05; F is 15:08.
  2. **Orders:** market only; no limit, stop, target or bracket.
  3. **D9.3:** at most 1 entry a day; holds at least 10 minutes.
  4. **D9.4:** one trade a day. The entry follows a closed 5-minute block, not a reopen or a release
     minute.
  5. **News (D9.5):** q_c <= 1 lot-equivalent, never the full maximum. A position may span the 13:00
     FOMC statement.
  6. **D9.5a:** no entry fill in [13:00, 13:02) (C6). The 07:30 Employment and CPI guards fall
     before the first possible fill. A fill in [13:00, 13:30) pays D8's event-window cost.
  7. **D9.6:** GC at 1 lot, or MGC at <= 10 contracts = 1 lot.
  8. **D9.7:** gold per C12.
  9. **D9.8 (star):** MGC\* if D2 chooses it. **D9.11:** GC's cap of 3 and MGC's cap of 30 (50K)
     do not bind below the 1-lot cap. **D9.12:** CPI window [07:25, 07:35]; no fill is possible
     there, since the first fill is at 08:35.
  10. **D9.13:** early-close dates are excluded (C5).
- **Member-level coverage (D9, C13):** the gold vehicle from 08:35 to 15:05 CT. D1 measured gold
  only in 07:20-12:30, so E.2 checks 12:30-15:05. MES's RTH coverage was 1.000 (D1 table).
- **Data needed:** MES ohlcv-1m (owned) and the gold vehicle's ohlcv-1m.
  - **Research window:** 2025-04-01..2026-06-19.
  - **Confirmation window:** [max(S_gold, 2020-02-03), 2024-02-29], the D4 intersection with MES's
    S from D.1f.
- **Source window and label:** the source's sample is 2007 to 2018 (P-K8-003-a). It does not overlap
  a confirmation window that starts no earlier than 2020-02-03, so there is no "source-overlap"
  label.
- **Trials in N:** 2 (H30, HEOD).

### K8-oilcad-01 (crude leads the Canadian dollar by one 5-minute step)
- **Cluster** K8.
  - **Signal leg:** WTI crude (K4), read on the crude exposure's price-path series (C9).
  - **Traded leg:** CAD (K3). The only admissible contract is 6C (D1 table).
  - **Vehicle:** D2 (chosen in E.2), which can only be 6C. Traded only if D2 admits CAD.
- **Mechanism:** a large 5-minute move in crude is followed, over the next 5 minutes, by a move of
  CAD against the dollar in the same direction. Causality runs "in the direction of commodity price
  to exchange rate, at horizon one" in 5-minute WTI and CAD/USD data (P-K8-006-a, P-K8-006-b,
  P-K8-006-d). On the direction: "higher oil prices are associated with a depreciation of the U.S.
  dollar ... particularly strong against ... the Canadian dollar" (P-K8-001-e). CAD has the largest
  post-2008 coefficient of the currencies in K8-001's Table 5, 0.090 (P-K8-001-f). New to the
  program.
  - **Conflicting and limiting evidence:**
    - The source itself: "There is weak evidence of Granger-causality in both directions ... The
      measures drop quickly after horizon one" (P-K8-006-b).
    - The measured intensities are tiny: the log's note on Figure 11 gives a chart axis topping at
      0.0024 ([unverified] as values).
    - The 5-minute sample is 2005-2009, from CQG; whether it is spot or futures is [unverified]
      (P-K8-006-a, P-K8-006-e). The source has no out-of-sample test and no costs (K8-006 block).
    - K8-001 finds CAD's response to the WPSR oil shock inside its 15-minute window, and its
      5-minute window gives estimates "very close to the benchmark" (P-K8-001-h). On release days
      the response therefore looks complete within minutes, which leaves little for a one-step lag
      after the block closes.
    - Whether the lead now resolves within seconds is unknown: the log measures it only at the
      5-minute sampling unit. Rule 7 excludes a lead that resolves in seconds; the logged evidence
      shows no such thing, so the member is kept. If the lead does resolve inside the block, the
      member comes out null, and that is its falsification.
- **Signal (on the crude series, K4 clock):**
  - **Decision times:** T = {08:05, 08:10, ..., 13:25} CT, 65 a day. Each covers the block [t - 5, t).
  - **Block return:** r_t = (C_cl(t - 1) - C_cl(t - 6)) / C_cl(t - 6). The denominator must be
    positive (K4 catalog C10), and both bars must carry one instrument_id.
  - **Scale:** s(d) = the sample standard deviation of all defined r_t (t in T) on the 20 most recent
    earlier eligible dates of the same window (C5). n >= 1,000 is required (the maximum is 1,300);
    otherwise there is no trade on d.
  - **Standardized move:** z_t = r_t / s(d).
- **Entry rule:**
  - At t in T, enter if all three hold: the member has no open position; no exit of its own is
    pending at t; and |z_t| >= 2.0.
  - The intent is a market intent on the 6C bar at t - 1, filling at the open of the 6C bar at t.
    BUY if z_t > 0 and SELL if z_t < 0. 6C is quoted in USD per CAD (K3 catalog C8), so a stronger
    CAD is a higher 6C.
  - C6 applies (FOMC at 13:00; WPSR at T_W on release days). On a standard WPSR day the 09:30
    decision, whose block is pre-release, is skipped. The 09:35 decision, whose block holds the
    release response, is not.
- **Exit rule:** market intent on the 6C bar at T_e + 14, filling at the open of T_e + 15 (T_e is
  the entry fill minute).
- **Holding horizon:** 15 minutes. **Session window:** 08:05-13:40 CT. **Flat by F:** 6C's F is 15:08
  (D6 FX row); the last fill is at 13:40.
- **Data fields read:**
  - **Crude series ohlcv-1m close and instrument_id**, bars 07:59..13:24 CT on d and on the 20
    warm-up dates. Databento GLBX.MDP3, paid. CL has history 2019-05..2026-06; MCL only from
    2021-07-12 (C9). Available at each bar's close.
  - **6C ohlcv-1m open and instrument_id**, 08:05..13:40 CT. Paid; history 2019-05..2026-06.
  - **EC-CAL** (energy and FX groups), and **EC-FOMC, EC-BLS and EC-WPSR** (for C6 only). Free,
    known before d.
- **Order type:** market. **Sizing:** q_c of 6C. That is 1, the cap for a full-size-only exposure,
  and D2 may flag it "undersized". The crude leg takes no position.
- **Parameters:**
  - **5-minute block and one-step horizon:** K8-006's sampling unit and its "horizon one"
    (P-K8-006-a, P-K8-006-b).
  - **Blocks inside 08:00-13:30 CT (judgment):** the energy day session (D6 table: O 08:00, C 13:30),
    which lies inside 6C's day session (O 07:20, C 14:00). K8-006 does not state the session hours
    of its 5-minute series.
  - **|z| >= 2.0 (judgment).** K8-006 fits a linear VAR, which has no threshold.
    - Two standard deviations select the largest few percent of blocks: 4.6% under a normal
      approximation, about 3 of the 65 a day.
    - Those are the blocks where a one-step spillover of a fixed fraction of the crude move is
      largest against 6C's fixed round-turn cost.
    - The cut also keeps entries far below the cap.
  - **20 trailing dates and n >= 1,000 (judgment):** as in K8-flight-01; 1,000 is about 77% of the
    maximum.
  - **Hold of 15 minutes (judgment).**
    - K8-001's benchmark response window is 15 minutes (P-K8-001-a, P-K8-001-b).
    - K8-006's measures last "only about one hour" in the 5-minute VAR (P-K8-006-c), but they sit
      mostly in the first step.
    - A 10-minute hold would sit exactly on D9.3(c)'s mean floor, where any shortened hold (a forced
      D9.7 exit) would fail it. 15 is the next multiple of the block length.
  - **Grid:** none.
- **Expected entries and holding:**
  - About 3 blocks a day pass the threshold under a normal approximation (arithmetic, not a data
    estimate). Entries are fewer, because of the busy skip.
  - At most 17 entries a day by construction. The 15-minute hold plus the pending-exit skip space
    entries at least 20 minutes apart within the 320 minutes from 08:05 to 13:25.
  - Every hold is 15 minutes.
  - **Floor:** at most 17 entries (limit 20); each hold is 15 minutes (at least 2 full minutes); the
    mean is 15 (at least 10). OK.
- **Falsification:**
  - **The standard condition,** on CAD's eps_X.
  - **Sign check (reported):** the mean over trades of sign(z_t) x (6C open at exit - 6C open at
    entry), in ticks and gross of cost, is positive.
  - **Descriptive split:** the same statistic for the 09:35 decision on standard WPSR days alone, and
    for all other decisions.
- **Topstep check (traded leg: 6C):**
  1. **Flat by F:** last fill 13:40.
  2. **Orders:** market only.
  3. **D9.3:** at most 17 entries a day; 15-minute holds.
  4. **D9.4:** entries at least 20 minutes apart; no stops, targets or brackets; not a queue-position
     or stray-fill strategy.
  5. **News:** q_c = 1 = 1 lot-equivalent, half the XFA maximum.
  6. **D9.5a:** no entry fill in a guarded interval (C6). On WPSR and FOMC days, fills in [release,
     release + 30 min) pay D8's event-window cost.
  7. **D9.6:** 6C counts 1 lot.
  8. **D9.7:** 6C per C12.
  9. **D9.8:** 6C is unstarred. **D9.11 and D9.12** name no FX product.
- **Member-level coverage (D9, C13):**
  - 6C, 08:05-13:40: inside D1's measured 07:20-14:00 window, where coverage was 0.985.
  - Crude, 07:59-13:24: the energy window of D1, coverage 1.000, except the single bar at 07:59.
- **Data needed:** ohlcv-1m of the crude series and of 6C.
  - **Research window:** 2025-04-01..2026-06-19.
  - **Confirmation window:** [max(S_crude, S_CAD), 2024-02-29].
- **Source window and label:**
  - K8-006: 2005-01-03..2009-12-31 for the 5-minute data (P-K8-006-a); 1986-2015 for the daily data
    (K8-006 block).
  - K8-001: 2003M10..2017M10 (P-K8-001-g).
  - No overlap, so no label.
- **Trials in N:** 1.

### K8-wkndbtc-01 (the weekend bitcoin move predicts the Monday Nasdaq-100 trade date)
- **Cluster** K8.
  - **Signal leg:** bitcoin (K7), read on MBT bars.
  - **Traded leg:** the Nasdaq-100 (K1). Admissible contracts: MNQ\* and NQ (D1 table).
  - **Vehicle:** D2 (chosen in E.2). Traded only if D2 admits the Nasdaq-100.
- **Mechanism:** a negative weekend move in crypto is followed by a weaker Monday for stocks.
  "negative cryptocurrency returns and increased volatility during weekends predict poorer stock
  market performance on Mondays, an effect that became particularly evident following the LUNA crash
  in mid-2022" (P-K8-004-b). The paper studies "how cryptocurrency weekend returns and volatility
  affect Monday stock returns" with a Bayesian regression and a Kalman filter (P-K8-004-a). New to
  the program.
  - **Evidence status:** abstract only, from a 17-page working paper (K8-004). The following are
    [unverified]: which stock indexes, cash or futures, the definition of the Monday return, the
    crypto series, the sample and costs. The dependence on a regime (after LUNA) is itself a
    stability warning.
  - **Reasoned transfer (not tested by the source).**
    - **The weekend move is read from CME's bitcoin futures:** MBT's change from Friday 14:59 to
      Sunday 17:59 CT. MBT is "0.10 bitcoin, as defined by the CME CF Bitcoin Reference Rate (BRR)"
      (liquidity JSON), so it tracks the bitcoin price the source's crypto returns measure, up to
      changes in the basis.
    - **What remains tradeable:** the XFA cannot hold over the weekend, and the equity futures'
      Sunday reopening gap cannot be traded. If the source's Monday return runs from the Friday close
      ([unverified]), part of its effect sits in that gap. The member tests what remains of the
      Monday trade date after Sunday 18:00 CT.
    - **Scope:** only the return part is used. The volatility part is excluded (X-10).
  - **Choice of traded exposure (judgment): the Nasdaq-100.**
    - The source's "stock market" is [unverified]. Its most likely referent, the S&P 500, is not a
      traded exposure (D1.5).
    - Of the three IN K1 exposures, the Nasdaq-100 is, like the S&P 500, a capitalization-weighted
      large-cap index. The Dow is a price-weighted 30-stock index and the Russell 2000 a small-cap
      index.
    - It is also the most liquid (MNQ ADV 2,363,465).
    - RTY and YM are not written (X-11).
- **Signal (on MBT, K7 clock):**
  - **Prices:** P_F = C_MBT(14:59) on the Friday immediately before Monday trade date d;
    P_S = C_MBT(17:59) on the Sunday that opens d.
  - **Validity:** both bars present with one instrument_id, and the Friday a full trade date in EC-CAL
    (equity-and-crypto). Otherwise there is no trade.
  - **Signal:** G = P_S / P_F - 1. If G = 0, there is no trade.
  - **Both regimes:** before 2026-05-29 the interval spans CME's weekend closure, and the Sunday
    17:59 close comes after one hour of trading following the 17:00 reopen. After 2026-05-29
    16:00 CT the interval spans continuous trading (C3). The definition is the same in both regimes,
    and it reads no bar outside a program trade date.
- **Entry rule:** on Monday trade date d, market intent on the Nasdaq-100 vehicle's bar at 17:59 CT
  Sunday, filling at the open of its 18:00 bar. BUY q_c if G > 0; SELL q_c if G < 0.
- **Exit rule:** market intent on the vehicle's bar at 14:58 CT Monday, filling at the 14:59 open.
  This is the C - 2 convention of D6's CP1, with C = 15:00.
- **Holding horizon:** 20 h 59 min. **Session window:** Sunday 18:00 to Monday 14:59 CT, inside one
  trade date (C3). **Flat by F** (15:08): the last fill is at 14:59.
- **Exclusions (in addition to C5):**
  - Monday trade dates that EC-CAL marks as early halt or closure. These are the US holiday Mondays;
    in the research window 2025-05-26, 2025-09-01, 2026-01-19, 2026-02-16 and 2026-05-25.
  - Monday trade dates whose preceding Friday is not a full trade date, for example Good Friday.
- **Data fields read:**
  - **MBT ohlcv-1m close and instrument_id**, at Friday 14:59 (available at 15:00 Friday) and at
    Sunday 17:59 (available at 18:00 Sunday). Databento GLBX.MDP3, paid. History from 2021-05-03
    only (listing; D13), so there are **no signal data for 2019-05..2021-04.**
  - **Nasdaq-100 vehicle ohlcv-1m open and instrument_id**, at Sunday 18:00 and Monday 14:59. Paid;
    NQ from 2019-05, MNQ from 2019-05-06.
  - **EC-CAL** (equity-and-crypto group). Free, known in advance.
- **Order type:** market. **Sizing:** q_c of the Nasdaq-100 vehicle (NQ: 1; MNQ: <= 10). The MBT leg
  takes no position.
- **Parameters:**
  - **P_F at Friday 14:59 (judgment):** the last minute of the US cash session (08:30-15:00 CT), so G
    starts when the stock market closes for the weekend. The source's starting point is [unverified].
  - **P_S at Sunday 17:59, entry at 18:00 (judgment).**
    - One hour after CME's Sunday 17:00 CT reopen (Topstep F4 "Sunday open | 5:00 PM CT"), the entry
      is clear of the reopen's first minutes. Those minutes are the gapped market of D9.4, as the K7
      catalog's X-01 reads [F7.2].
    - 18:00 CST is 00:00 UTC Monday, the usual end of a weekend in daily UTC crypto data. In CDT,
      18:00 CT is 23:00 UTC. The source's clock is [unverified].
  - **Symmetric sign (judgment).** The source's model relates Monday returns to weekend returns
    (P-K8-004-a), and its abstract states the negative side (P-K8-004-b). A linear reading predicts
    both signs. The negative side is reported separately (see Falsification).
  - **Exit at 14:59:** D6's C - 2 convention for the equity group.
  - **Grid:** none.
- **Expected entries and holding:**
  - At most 1 entry a week: Monday trade dates only, about 0.2 per trade date.
  - About 58 Mondays in the research window after the holiday Mondays (63 - 5). At most 148 in the
    confirmation window from 2021-05-03, before holiday, roll, missing-bar and start-rule exclusions
    (C11).
  - Each hold is 20 h 59 min.
  - **Floor:** OK.
  - **Power:** likely "inconclusive by design" under D4 (question 2).
- **Falsification:**
  - **The standard condition,** on the Nasdaq-100's eps_X.
  - **Sign check (reported):** the mean of sign(G) x (vehicle open at 14:59 - open at 18:00), in
    ticks, is positive.
  - **Splits (descriptive):** by the sign of G, since the abstract's claim is for G < 0; and by
    period, before and after 2022-06-30, since the abstract says the effect appeared "following the
    LUNA crash in mid-2022".
- **Topstep check (traded leg: the Nasdaq-100):**
  1. **Flat by F:** last fill 14:59. The position opens after Topstep's "Sunday open | 5:00 PM CT"
     (F4) and stays inside one trade date.
  2. **Orders:** market only.
  3. **D9.3:** 1 entry a week.
  4. **D9.4:** the entry comes 60 minutes after the reopen; it is not a stray-fill trade in a gapped
     market.
  5. **News:** q_c <= 1 lot-equivalent, never the full maximum. The position spans the Monday 07:30
     releases and any later ones.
  6. **D9.5a:** no fill in a guarded interval; the fills are on Sunday at 18:00 and Monday at 14:59.
  7. **D9.6:** NQ at 1, or MNQ at <= 10.
  8. **D9.7:** equity-index limits bind on Sunday evenings after large weekend news. The harness
     blocks the entry, and forces the exit, beyond the stop level (C12).
  9. **D9.8:** MNQ\* if D2 chooses it (referent D9.12). **D9.12:** no opening fill falls in a CPI
     window, since entries are only at 18:00 on Sundays. **D9.11** names no equity product.
- **Member-level coverage (D9, C13):**
  - The Nasdaq-100 vehicle at Sunday 18:00 and Monday 14:59. D1 measured only 08:30-15:00, so the
    Sunday-evening minute is E.2's check.
  - The MBT signal bars at Friday 14:59 and Sunday 17:59 (C13).
- **Data needed:** MBT and Nasdaq-100 vehicle ohlcv-1m, including the Sunday-evening Globex bars.
  - **Research window:** 2025-04-01..2026-06-19. Three of its Mondays (2026-06-01, 06-08, 06-15)
    fall after the 24/7 change.
  - **Confirmation window:** [max(S_MBT, S_Nasdaq), 2024-02-29], with S_MBT >= 2021-05-03.
- **Source window and label:** the sample is [unverified]. It includes mid-2022 and later
  (P-K8-004-b; the paper was posted on 6 Aug 2025), so it overlaps the confirmation window. The member
  is labelled **"source-overlap"** (NULL_CRITERIA_E section 3). A null statement is unaffected, but no
  edge on it could be claimed without a registered holdout read.
- **Trials in N:** 1.

### K8-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: 6C only; if 6C is not admitted, no ML member (the mechanism is crude to CAD).]
- **Traded vehicle: CAD {6C}.** Traded only if D2 admits CAD.
  - **Why CAD:** it is the exposure the K8 log supports most.
    - Both of the log's full-text directional sources name it. K8-006 has the log's only 5-minute
      lead, crude to CAD (P-K8-006-a, P-K8-006-b). In K8-001, CAD has the largest post-2008 response
      of the currencies to the WPSR oil shock (P-K8-001-e, P-K8-001-f).
    - The partition names "crude and CAD" as a K8 relationship (section 3).
    - The alternatives rest on less. Gold rests on one abstract (K8-003). The Nasdaq-100 rests on one
      abstract (K8-004) plus contemporaneous or off-universe evidence (K8-001, K8-002, K8-007).
  - **Contract:** 6C is CAD's only admissible contract (D1 table; ADV 81,946).
  - **No fallback is declared.** If D2 does not admit CAD, the lead decides.
- **Products the features read:**
  - 6C, its own bars: B1-B5 and KF5.
  - The crude series (K4, C9): KF1, KF2, KF4 and KF5. Crude is named by K8-006 and K8-001.
  - MES (K1): KF6. The S&P 500 is named by K8-006 as its conditioning series and by K8-001 as a
    responding market.
  - Calendars: EC-WPSR (KF3, KF4) and EC-CAL (FX, energy, equity-and-crypto groups).
- **Cluster features (6; with D15.4's B1-B5 the total is 11).** Notation:
  - t_j is the decision time; the last bar closed at t_j is the bar at t_j - 1.
  - C_X(tau) is the close of leg X's bar at tau.
  - Returns are in basis points (10,000 x the fraction), so they are the same on any contract of a
    leg.
  - A missing bar, or a change of instrument_id inside one feature's bars, means no trade at t_j
    (D15.4).

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | cl_ret5 | 10,000 x (C_cl(t_j - 1) - C_cl(t_j - 6)) / C_cl(t_j - 6) | K8-006 P-K8-006-a, P-K8-006-b (5-minute data; the lead is at horizon one) | t_j (the bar at t_j - 1 has closed) |
| KF2 | cl_ret60 | 10,000 x (C_cl(t_j - 1) - C_cl(t_j - 61)) / C_cl(t_j - 61) | K8-006 P-K8-006-c (causality measures over 11 five-minute lags, "only about one hour") | t_j |
| KF3 | wpsr_phase | If d is an EC-WPSR release date with scheduled time T_W(d) (C10, the schedule known the evening before d): -1 if t_j < T_W(d), +1 if t_j >= T_W(d). Otherwise 0 | K8-001 P-K8-001-a, P-K8-001-b (WPSR news moves crude, and CAD with it, inside the release window) | calendar, known before d |
| KF4 | cl_wpsr | If KF3 = +1 and t_j >= T_W(d) + 10: 10,000 x (C_cl(T_W + 9) - C_cl(T_W - 6)) / C_cl(T_W - 6), the crude return over [T_W - 5, T_W + 10]. Otherwise 0. The 0 is a fixed literal (no release, or its window has not closed), not an imputation. A missing bar inside the window means no trade at t_j | K8-001 P-K8-001-b (the [-5; +10]-minute window); P-K8-001-e, P-K8-001-f (the CAD response) | T_W + 10 |
| KF5 | cad_gap30 | 10,000 x [(C_6C(t_j - 1) - C_6C(t_j - 31)) / C_6C(t_j - 31) - 0.090 x (C_cl(t_j - 1) - C_cl(t_j - 31)) / C_cl(t_j - 31)]: CAD's 30-minute move minus the move implied by crude's | K8-001 P-K8-001-f (0.090, the post-2008M9 CAD coefficient, a return-on-return coefficient: see the preamble) and P-K8-001-h (the estimate holds on a 30-minute window); K8-006 P-K8-006-b (direction: crude to CAD) | t_j |
| KF6 | es_ret30 | 10,000 x (C_MES(t_j - 1) - C_MES(t_j - 31)) / C_MES(t_j - 31) | K8-006 P-K8-006-d, P-K8-006-e (the S&P 500 is the conditioning series of the 5-minute analysis); K8-001 P-K8-001-c (the stock market moves with oil in the release window) | t_j |

  - The literal 0.090 is fixed here. It is not estimated on any window (D15.4).
  - No feature reads a released inventory value, a settlement price, or anything published after
    t_j.
  - B1-B5 are computed on 6C. B3 is minutes since O = 07:20 (D6 FX row).
- **Decision window [W0, W1] = [08:10, 12:55] CT; horizon h = 15 minutes.**
  - **Decision times:** 08:10, 08:25, ..., 12:55, which is 20 a day. W1 + h = 13:10, before
    F = 15:08.
  - **Fills (D15.3, D15.6):** entries at t_j + 1 (:11, :26, :41, :56); exits at t_j + h (:25, :40,
    :55, :10).
  - **Why this window:**
    - It starts after the energy day-session open (08:00, D6), so KF1 reads day-session crude from
      the first decision. It also starts after the 07:30 BLS releases.
    - The :10/:25/:40/:55 grid makes t_j = 09:40 = T_W + 10 on standard WPSR days, the first decision
      at which KF4 exists. For exception releases at 10:00 or 11:00 CT, T_W + 10 = 10:10 or 11:10 is
      also a decision time.
    - No fill falls in [:00, :02) or [:30, :32). None therefore meets the D9.5a interval of the
      07:30, 09:30, 10:00, 11:00 or 13:00 releases (C6).
    - W1 = 12:55 gives the 20 decisions the cap allows. On statement days the last position
      (12:56-13:10) spans the FOMC statement without a fill in its guarded interval.
    - The window lies inside 6C's day session (07:20-14:00) and crude's (08:00-13:30).
  - **Why h = 15:** the smallest value on the menu, and the one nearest the logged horizons.
    - K8-006's lead is one 5-minute step, and its measures fade within "about one hour"
      (P-K8-006-b, P-K8-006-c).
    - K8-001's benchmark window is 15 minutes (P-K8-001-a, P-K8-001-b).
    - h = 30 or more would dilute a one-step lead with minutes the log gives no reason to hold, and
      would allow at most 10 decisions in the window.
- **Expected rows:** 20 per eligible research-window trade date. From about 305 trade dates, remove
  6C's roll-blackout dates, early-halt dates, vendor-degraded dates and B4's 20-date warm-up; about
  260-270 dates remain. That gives about 5,200-5,400 rows; E.2 gives the exact count.
- **Expected entries:** at most 20 a day, each held 15 minutes. The floor holds by construction.
- **Falsification:** the standard condition: UCB95 of the mean net daily P&L per contract of 6C below
  CAD's eps_X, at >= 80% achieved null power on the confirmation window, counts against it. Failing
  the D5 screen puts the member in Tier B.
- **Topstep check (6C):**
  1. **Flat by F:** last exit 13:10.
  2. **Orders:** market (D15.6).
  3. **D9.3:** at most 20 entries a day; 15-minute holds.
  4. **D9.4:** no stops or brackets; no fill in a release minute.
  5. **News:** q_c = 1 lot-equivalent.
  6. **D9.5a:** no fill in any guarded interval, by construction. On WPSR days, the fills at 09:40,
     09:41, 09:55 and 09:56 pay D8's event-window cost; on FOMC days, the 13:10 exit does.
  7. **D9.6:** 1 lot.
  8. **D9.7:** 6C per C12.
  9. **D9.8:** 6C is unstarred. **D9.11 and D9.12** name no FX product.
  10. **D9.9:** the "Unfair technology ... AI" line is flagged for the user, as the design does for
      every ML member.
- **Data needed:** ohlcv-1m of 6C, the crude series and MES.
  - **Training and tuning:** on the research window only (MES's research parquet; the other legs are
    bought in E.1).
  - **The frozen model:** runs on the confirmation window [max(S_CAD, S_crude, 2020-02-03),
    2024-02-29].
  - **Coverage (C13):** 6C 08:11-13:10; crude 07:09-12:54 (KF2 at 08:10 reads the crude bar at
    07:09, before the energy day session); MES 07:39-12:54.
- **Source window and label:** K8-001 covers 2003M10..2017M10; K8-006 covers 2005-2009 (5-minute)
  and 1986-2015 (daily). No overlap, so no label.
- **Trials in N:** 1 at confirmation. In the K8 screening session's research-window accounting the
  grid counts as 48 (D15.8).
- **Not chosen here (D15):** the model type, grid, selection rule and trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K8-wpsrcad-01 | 6C traded from T_W + 10 on the sign of crude's [T_W - 5, T_W + 10] return, held 15-30 minutes (K8-001 P-K8-001-b, e, f) | Rule 1 (evidence) | K8-001 measures CAD's response inside the release window and tests no lag. Its 5- and 30-minute windows give point estimates "very close to the benchmark" (P-K8-001-h), so the logged evidence places the whole response inside the window, with no documented move after T_W + 10. The release response enters K8-ml-01 (KF3, KF4), and K8-oilcad-01's 09:35 decision covers the one-step case |
| X-02 K8-wpsreq-01 | NQ, RTY or YM traded after the WPSR on crude's release-window return (P-K8-001-c: +1.1% per +10% oil after 2008) | Rule 1 | The relation is contemporaneous and no lag is measured. The equity leg is SPY and sector ETFs, not NQ, RTY or YM (K8-001 legs line). The sign flips at 2008M9 (-0.8% before, +1.1% after, P-K8-001-c), so the relation is unstable |
| X-03 K8-wpsrzn-01 | ZN, ZF or ZT traded after the WPSR on crude's return (P-K8-001-d) | Rule 1 | Contemporaneous. After 2008 the 10-year yield moves "0.7 bps" per +10% oil, and the shorter tenors are "statistically insignificant" (P-K8-001-d). The authors call the bond effects economically small (K8-001 quality tells) |
| X-04 K8-oilcomfx-01 | 6A and 6N (and 6E, 6B) traded on crude's 5-minute moves, as in K8-oilcad-01 | Rule 1 | The 5-minute evidence is "available for Canada only" (P-K8-006-a). K8-001's coefficients for AUD, NZD, EUR and GBP (P-K8-001-f) are contemporaneous. K8-006's AUD result is daily (K8-006 block) and has X-05's problem |
| X-05 K8-oilcadday-01 | 6C traded in the day session on the sign of crude's prior-day return (K8-006's daily "horizon one", P-K8-006-d) | Rule 3 (timing); rule 1 | The daily series come from different publishers: CAD/USD "from Statistics Canada" and WTI "from Energy Information Administration" (the K8-006 Table 1 note, in the reader's copy; preamble). Their sampling times are not stated and are not shown to be one clock, so a one-day "lead" can come from the sampling offset alone. A rule on synchronized CME bars would be a new test with no logged horizon. The synchronized 5-minute version is K8-oilcad-01 |
| X-06 K8-apieq-01 | NQ, RTY or YM traded 08:30-08:40 CT on Wednesday in the direction of crude's post-API return (Tuesday 15:30-16:00 CT) (K8-002 P-K8-002-a, b, c) | Rule 1; D9.3(c) margin | The responding leg is energy stocks and the NYSE Arca Oil and Gas Index (P-K8-002-c), which are off-universe. The implication for index futures is untested (K8-002 tags), and in a broad index the effect would be diluted by the energy sector's weight. The documented window is 10 minutes, exactly the D9.3(c) mean floor. The crude-only part of the same paper is covered by K4-apipre-01 |
| X-07 K8-oilvol-01 | a crude or equity-index member gated by the other market's 5-minute volatility, spread or volume (K8-007 P-K8-007-a, b) | Rule 1 | Abstract only. The predicted quantity is volatility, not direction, and the "utility gains" are mean-variance certainty equivalents, not net P&L (K8-007 quality tells). A gate needs a base member on crude or an equity index; K8 has none, and K4 and K1 own their own base members |
| X-08 K8-eqopenzn-01 | ZN traded after 08:30 CT in the direction implied by MES's first 30 minutes (K8-008) | Rule 1 | The source measures information shares, not returns (P-K8-008-a, P-K8-008-b). Its link to "returns and net order flows of the US stock market" appears only in the published abstract, with no sign ([unverified] content; P-K8-008-c). The manuscript's state-space check finds "little variation" (P-K8-008-d). ZN's own post-open window is covered by K2-ml-01 (eqopen_ret, from K2-017, the same paper) |
| X-09 K8-flightpost-01 | gold bought at the US stock close on extreme-decline days and held for the "post US stock trading hours" rise (P-K8-003-b) | Flat by F (D9.1) | The continuation comes after 15:00 CT. The XFA allows only the minutes up to 15:08 and no overnight hold. The in-session lead-in is K8-flight-01's HEOD point |
| X-10 K8-wkndvol-01 | a Monday Nasdaq-100 short after high weekend crypto volatility (P-K8-004-b, "increased volatility") | Rule 3; partition section 1 | Before 2026-05-29 CME has no weekend bitcoin bars (C3), so weekend volatility needs spot intraday data. Coinbase's candles are free (K7 catalog preamble and C10), but a non-CME signal for a K1 product belongs to K1's region (partition section 1), not K8's. The source's volatility measure is [unverified] |
| X-11 K8-wkndbtc-01 variants | (a) the same rule on RTY and on YM (+1 trial each); (b) the short-only reading (trade only G < 0); (c) entry at the Monday 08:30 CT cash open instead of Sunday 18:00 | Rule 11 (no padding); judgment | One trial is proportionate for an abstract-only source. (a) The source's index is [unverified], and the Nasdaq-100 was chosen with a reason (K8-wkndbtc-01). (b) is a subset of K8-wkndbtc-01's trades and is reported there as a split. (c) is a sub-interval of the same holding window. The lead may add any of them |
| X-12 K8-cadcl-pair-01 | an intraday crude-CAD spread (F19, Milton FMR) | D2 and rule 5; rule 1 | Two legs at full size are 2 lot-equivalents, and MCL plus 6C is 1.1 (6C has no admissible micro). The logged source is a daily cointegration trade with multi-day holds (R-K8-014) |
| X-13 K8-fomcsurp-01 | gold, 6E, 6J or CL traded on the FOMC target or path surprise measured from fed funds futures. Routed by the K3 catalog (X-06, K3-009), the K4 catalog (Rosa, K4-025) and the K5 catalog (K5-024) | Rule 1 (not in the K8 log); rule 3 | These routings came from catalogs written after the K8 log closed, and the K8 log holds no passage for them. The surprise needs CBOT 30-day fed funds futures bars, a product outside Topstep's list and outside the D13 purchase plan, so a quote would be needed. On the evidence in the other logs: gold's continuation is covered by K5-fomc-01 (gold's own first five minutes as the surprise proxy); the FX reaction is "short-lived" (P-K3-009-a); Rosa's dollar channel is contemporaneous (F13). See question 7 |
| X-14 K8-mpucond-01 | FX or crude macro-release responses conditioned on monetary-policy uncertainty (K3-035, routed by the K3 and K4 catalogs) | Rule 1; rule 3 | Not in the K8 log, and abstract only. The uncertainty measure is [unverified], with no free historical source named. No cluster has a macro-release base member to condition (K3 X-05) |

---

## 3. Beyond budget

None. 4 of the 15 slots are used. No member was dropped for budget. The variants considered and not
written are in section 2 (X-11), each with its reason, and the lead may add any of them.

---

## 4. Log accounting

**Passed items (log section 4).**

| Item | Disposition |
|---|---|
| K8-001 Alquist, Ellwanger, Jin (full text) | **Used.** K8-oilcad-01: direction and the choice of CAD (P-e, P-f), with P-h as conflicting evidence. K8-ml-01: KF3 (P-a, b), KF4 (P-b, e, f), KF5 (P-f, h), KF6 (P-c). **Excluded as standalone members:** X-01 (6C on the release window), X-02 (equity index), X-03 (Treasuries), X-04 (6A, 6N, 6E, 6B). All are contemporaneous, with no lag measured |
| K8-002 Alturki, Kurov (full text, dissertation) | **Excluded:** X-06 (the responding leg is off-universe). The crude-only part is **covered by K4-apipre-01** |
| K8-003 Baur, Kuck (abstract only) | **Used:** K8-flight-01 (P-a, b, c). The post-close part is **not intraday-feasible** (X-09) |
| K8-004 Mourey, Shahrour, Soiman (abstract only) | **Used:** K8-wkndbtc-01 (P-a, b). The volatility part is excluded (X-10); variants in X-11 |
| K8-005 Buccheri, Corsi, Peluso | Did not survive in the log (not cross-cluster; R-K8-040). Not used |
| K8-006 Zhang, Dufour, Galbraith (full text) | **Used.** K8-oilcad-01 (P-a, b, c, d, e). K8-ml-01: KF1 (P-a, b), KF2 (P-c), KF5 (P-b), KF6 (P-d, e). The daily version is excluded (X-05); the other currencies too (X-04) |
| K8-007 Phan, Sharma, Narayan (abstract only) | **Excluded:** X-07 (no direction; needs a base member) |
| K8-008 Indriawan, Jiao, Tse (manuscript) | **Excluded:** X-08 (no direction). ZN's own post-open window is **covered by K2-ml-01** (eqopen_ret) |

**Routed flags (log section 1).**

| Flag | Item | Disposition |
|---|---|---|
| F01 | Kurov, Olson, Wolfe (2024) | Insufficient evidence: rejected in the log (R-K8-001; contemporaneous causal effects, no lead) |
| F02 | Zangelidis, Rezitis (2026) | Insufficient evidence (R-K8-002; volatility topology on daily realized volatility) |
| F03 | Sharma (arXiv 1705.08022) | Not intraday-feasible (R-K8-003; the macro variables' frequency). The K2 and K3 catalogs routed the same item; same disposition |
| F04 | Alquist, Ellwanger, Jin | **Used:** see K8-001 |
| F05 | K2's note to search rates-equity and rates-energy | Handled in containers 2 and 5. The only rates result is K8-001's contemporaneous bond response (X-03) |
| F06 | Aligrithm cross-asset series | Not intraday-feasible (R-K8-004; monthly or daily sources) |
| F07 | Peng, Chollete, Hughen (2026) | Insufficient evidence (R-K8-005; mixed-frequency volatility forecasting) |
| F08 | Quantpedia currency-spillover slugs | Insufficient evidence (R-K8-006; pages unreachable; the described source is monthly) |
| F09 | K3-001 ownership (Melvin and Prins) | **Covered by K3-mehedge-01.** Ownership is reserved for the lead (question 8) |
| F10 | Alturki, Kurov | See K8-002: excluded (X-06); covered by K4-apipre-01 |
| F11 | Quantpedia "Crude Oil Predicts Equity Returns" | Not intraday-feasible (R-K8-007; monthly) |
| F12 | Hao, He, Ma (2023) | Insufficient evidence (R-K8-008; volatility spillover, no return lead) |
| F13 | Rosa (2013), K4-025 | Excluded (X-13): contemporaneous dollar channel; K4-025 is read by K4 |
| F14 | Nowak, Anderson (2014) | Insufficient evidence (R-K8-009; single stocks) |
| F15 | Wu, Guan, Myers (2010) | Insufficient evidence (R-K8-010; volatility spillover, no intraday horizon) |
| F16 | energy-grain volatility spillover items | Insufficient evidence (R-K8-011; volatility) |
| F17 | Chiang, Hughen (2017) | Not intraday-feasible (R-K8-012; monthly) |
| F18 | Quantpedia "Financialization of crude oil market" | Insufficient evidence (R-K8-013; variance decomposition) |
| F19 | Milton FMR CAD-crude pairs | Not intraday-feasible (R-K8-014; daily, multi-day holds). A spread would also fail D2 (X-12) |
| F20 | arXiv 1209.0900, 1210.6080 | Not intraday-feasible (R-K8-015; low frequency) |
| F21 | gold against the dollar and real rates (no source pinned) | Insufficient evidence: the six container-3 queries produced no passing item (log section 2) |
| F22 | Wright Blogs "Metals as Macro Signals" | Insufficient evidence (R-K8-016) |
| F23 | Baur, Kuck | **Used:** K8-flight-01 |
| F24 | Semeyutin, Gozgor, Lau (2021) | Insufficient evidence (R-K8-017; contemporaneous co-jumps) |
| F25 | arXiv 2409.08355 | Not intraday-feasible (R-K8-018; low frequency) |
| F26 | Quantpedia gold regimes | Insufficient evidence (R-K8-019) |
| F27 | Ebrahimi, Ferris (2025) | Not intraday-feasible (R-K8-020; monthly horizon) |
| F28 | CME OpenMarkets soybean oil and crude | Not intraday-feasible (R-K8-021; a lead of months) |
| F29 | CME energy demand and the soybean complex | Insufficient evidence (R-K8-022) |
| F30 | CME grains and equities in downturns | Insufficient evidence (R-K8-023) |
| F31 | Cao, Heckelei, Ionici (2024) | Insufficient evidence (R-K8-024; single food stocks) |
| F32 | CFTC OCE agricultural swaps and equities | Insufficient evidence (R-K8-025) |
| F33 | CFTC OCE convective risk flows | Not intraday-feasible (R-K8-026; daily) |
| F34 | K6-032 (EPA and CARB) | Not K8's: the lead ruled that it stays in K6 |
| F35 | Conlon, Corbet, Oxley (2024) | Excluded: sentiment, shelved (rule 13; R-K8-027) |
| F36 | Kose et al. (2024) | Not intraday-feasible (R-K8-028; daily and weekly) |
| F37 | Aalborg et al. (2018) | Not intraday-feasible (R-K8-029; daily) |
| F38 | Mourey et al. | **Used:** K8-wkndbtc-01 |
| F39 | arXiv 2505.14655 | Insufficient evidence (R-K8-030; single stocks) |
| F40 | Krause (2026); Lee (2024) | Not intraday-feasible (R-K8-031; daily correlation regimes) |
| F41 | Shakourloo (2026) | Insufficient evidence (R-K8-032; no intraday horizon) |
| F42 | Joo (2023) | Not intraday-feasible (R-K8-033; daily hedge ratios) |
| F43 | Mazur (2024), K7-027 | Covered by the K7 log (K7-027). The flow substitution is daily; no K8 member |
| F44 | CME research on bitcoin, equities and gold | Insufficient evidence (R-K8-034; commentary) |
| F45 | Pinchuk, K7-026 | Covered by the K7 log (K7-026); rates enter there only as a control |
| F46 | Quantpedia bitcoin, gold and equity items | Not intraday-feasible (R-K8-035; daily or longer) |
| F47 | Alquist et al. (K2's mention) | Duplicate of F04 |

**Rejected container items R-K8-036 to R-K8-082:** rejected in the log, none passed, none used. The
items the log leaves to the lead are listed unchanged in question 10: R-K8-045, R-K8-048, R-K8-058
and R-K8-071.

**Routings from the other catalogs' "Routed to K8" sections** (written after the K8 log closed):

| Catalog | Rows | Disposition |
|---|---|---|
| K2 | Sharma; Alquist | = F03; = F04 |
| K3 | rows 1-4 (Alquist, Aligrithm, Peng et al., Quantpedia slugs) | = F04, F06, F07, F08 |
| K3 | row 5: K3-009 surprise (the K3 catalog's X-06) | Excluded, X-13 |
| K3 | row 6: K3-035 | Excluded, X-14 |
| K3 | rows 7-10 (Sharma, Rosa, Milton FMR, Zangelidis) | = F03, F13, F19, F02 |
| K4 | rows 1-13 (the reader's flags) | = F04, F10, F11, F01, F12, F13, F14, F15, F16, F17, F18, F19, F20 |
| K4 | row 6's addition (the FOMC surprise measure) | Excluded, X-13 |
| K4 | row 14: K3-035 [K4] | Excluded, X-14 |
| K5 | rows 1-7 | = F21, F22, F23, F24, F25, F26, F27 |
| K5 | row 8: K5-024 rate surprise | Excluded, X-13. The own-price version is covered by K5-fomc-01 |
| K6 | all rows | = F28-F33, F16, F20; K6-032 = F34 |
| K7 | all rows | = F35-F46. Its 24/7 note is used in C3 and K8-wkndbtc-01 |

---

## 5. Trial count table

| Member | Traded exposure (cluster) | Signal leg (cluster) | Trials at confirmation | eps | Confirmation window (D4 intersection) | Label |
|---|---|---|---|---|---|---|
| K8-flight-01 H30 | gold (K5) | S&P 500 on MES (K1) | 1 | gold eps_X | [max(S_gold, 2020-02-03), 2024-02-29] | none |
| K8-flight-01 HEOD | gold (K5) | S&P 500 on MES (K1) | 1 | gold eps_X | same | none |
| K8-oilcad-01 | CAD (K3) | crude (K4) | 1 | CAD eps_X | [max(S_crude, S_CAD), 2024-02-29] | none |
| K8-wkndbtc-01 | Nasdaq-100 (K1) | bitcoin on MBT (K7) | 1 | Nasdaq-100 eps_X | [max(S_MBT, S_Nasdaq), 2024-02-29], with S_MBT >= 2021-05-03 | **source-overlap** |
| ~~K8-ml-01~~ [excluded, U6] | CAD (K3) | crude (K4); S&P 500 on MES (K1) | 0 (E.0: 1 (48 in screening accounting)) | ~~CAD eps_X~~ | ~~[max(S_CAD, S_crude, 2020-02-03), 2024-02-29]~~ | none |
| **K8 total** | | | **5** if D2 admits gold, CAD and the Nasdaq-100 (2a_G + 2a_C + a_N in general) | | | |

**Notes:**
- Cumulative program N was 58 before Stage E. K8 adds its trials at confirmation.
- K8's Holm family (D5) contains the members that pass the K8 screening session's screen, plus
  K8-ml-01.
- Each member is stated under K8 only (NULL_CRITERIA_E section 8).

---

## 6. Questions for the lead

1. **Signal-leg windows and MES's start rule.** MES's own start rule gave S = 2020-02-03. Applied as
   the MES leg's window under D4, it cuts about nine months off K8-flight-01's and K8-ml-01's
   confirmation windows. MES bars for 2019-05..2020-01 are owned; the start rule dropped them because
   MES volume was thin in its first months. For a signal leg, bar presence is what matters, and C4's
   missing-bar rule already handles gaps.
   - Does a signal leg's window follow its own start rule, or only the traded leg's?
2. **MBT's short history (K8-wkndbtc-01).** MBT exists from 2021-05-03, and its start rule may move
   S later. The member will likely be "inconclusive by design". CME's full-size bitcoin futures (BTC,
   listed 2017-12) could serve as the signal leg for 2019-05..2021-04, but BTC is not in D13, so a
   quote would be needed.
   - Quote BTC, or accept the short window?
3. **Signal-leg roll blackouts (C5).** This catalog excludes only the traded leg's roll-blackout
   dates. For signal legs it relies on the one-instrument_id rule within each computation.
   - Keep this, or require the union of all legs' blackouts? The union would cost crude's monthly
     blackouts, about 3 dates a month, from K8-oilcad-01 and K8-ml-01.
4. **Signal-leg coverage (C13).** This catalog proposes a signal-leg coverage check: exclude before
   screening if fewer than 95% of decision times have all signal bars. D9's check is defined for the
   traded vehicle only.
   - Confirm or amend.
5. **Does the WPSR "concern" 6C?** D8 counts a release as concerning a product when any catalog
   member trading that product names it. By that wording, K8-ml-01's naming of the WPSR would give
   every 6C trial the WPSR event-window cost and the D9.5a guard on Wednesdays 09:30-10:00, K3's
   ports on 6C included.
   - Apply it program-wide (conservative, one cost model per product), or to K8's members only?
6. **C6's skip rule.** For entries whose fill would land in a D9.5a guarded interval, this catalog
   skips the entry instead of deferring it, because K8 signals are measured before the release.
   - Confirm that a member may adopt this rule, which is stricter than the harness default.
7. **FOMC-surprise routings (X-13).** The K3, K4 and K5 catalogs routed these after the K8 log
   closed. They need CBOT fed funds futures bars, which are not in D13.
   - Close them, or schedule a later K8 pass with a quote?
8. **F09 ownership (K3-001, Melvin and Prins).** This catalog records it as covered by
   K3-mehedge-01. The ownership decision is yours.
9. **K8-wkndbtc-01's choices.** The member trades the Nasdaq-100 only and takes the symmetric sign
   (X-11).
   - Add RTY and YM (+1 trial each)? Use the short-only reading?
10. **Items the K8 log leaves to the lead (unchanged):**
    - R-K8-045: Dobrev and Schaumburg, "High-frequency cross-market trading", not found.
    - R-K8-048: Iwanaga and Sakemoto (2026), K1's region, not in the registry.
    - R-K8-058: Geman and Li (2018), K4's region, not in the registry.
    - R-K8-071: Bu (2021), K4's region, not in the registry.
11. **The 24/7 regime (K8-wkndbtc-01).** The confirmation window lies entirely in the weekend-closure
    regime. Deployment would lie entirely in the continuous regime (from 2026-05-29). The signal's
    definition is unchanged, and the equity futures still close at weekends, so the rule stays
    deployable. But the Friday-to-Sunday MBT move changes from a closed-market gap to a traded return.
    - Say whether a confirmation result on the old regime is acceptable for this member.
12. **Judgment parameters.** These rest on abstract-level or threshold-free evidence:
    - K8-flight-01's 0.5% tail, 20-date lookback and 30-minute exit;
    - K8-oilcad-01's 2.0-sigma cut and 15-minute hold;
    - K8-wkndbtc-01's clock points (Friday 14:59, Sunday 17:59).

    If you prefer other fixed values, they must be set before hashing. None of these values came from
    data.

---
