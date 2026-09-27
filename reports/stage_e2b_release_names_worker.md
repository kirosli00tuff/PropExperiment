# ReleaseNamesExtractor-SonnetMed: worker report (Stage E.2b, g1a)

Time: 2026-09-26, PDT (TZ=America/Vancouver).

## Objective and scope

Extracted every scheduled release, report, statement or announcement named by any of the 64
members of the frozen Stage E catalog (`reports/stage_e0_catalog.json`, `reports/stage_e0_catalog_K1.md`
.. `_K8.md`, section "## 1. Members" only). Excluded members and features under "## 2. Excluded
members" in each K*.md (the X-01..X-15 style candidates) are NOT catalog members (catalog.json has
exactly 64 members, matching the "## 1. Members" headers across the 8 files) and were not extracted
as separate rows, even where they name additional releases (e.g. K5 log's X-03, X-14). No web
research was done; only the named files were read.

## Method

1. Split each K*.md file into its 64 member sections by `### <id>` headers under "## 1. Members"
   (verified boundaries against each file's "## 2. Excluded members" header line).
2. Grepped every section for the brief's term list (release, report, announcement, statement, FOMC,
   CPI, payroll, NFP, employment, EIA, inventor*, storage, USDA, WASDE, crop, cattle, hogs, auction,
   Treasury, ECB, BoE, BoJ, RBA, RBNZ, SNB, BoC, rate decision, minutes, GDP, PMI, ISM, retail sales,
   PPI, PCE, jobless, claims, OPEC, settlement, fix) plus London/Tokyo/BRR/G.17 clock names that the
   catalog itself uses for the same events.
3. Read every flagged section in full to classify each release mention as "signal" (the member's
   entry/exit or an ML feature times directly on the release/fix/auction/settlement clock) or
   "mentioned" (the release is named as a News/D9.5a/CPI-window constraint the member's rule holds
   through, avoids, or is built around, without timing its own action on it).
4. Verified every quote and line number by grep against the original catalog file (all 107 rows
   resolved to an exact line; no [unverified] rows).

## Output

- `reports/stage_e2b_release_names.json`: `{"members": [...107 rows...], "distinct_releases":
  [...18 releases...], "counts": {...}}`. Each member row: member_id, cluster, status (from
  catalog.json, e.g. "active" / "excluded_by_lead"), traded_products (catalog.json
  `starred_products`), read_products (catalog.json `exposures`), release_name_verbatim, quote
  (verbatim catalog line), source_file, line, role, note, in_f6_4.
- `reports/stage_e2b_release_names.md`: the same 107 rows as a sortable table.

## Counts

- 64 catalog members total; 60 name at least one release; 4 name none
  (K2-cp2-01, K2-monthend-01, K3-cp2-01, K7-montrend-01 — checked individually, no keyword hits).
- 107 member-x-release rows: 46 "signal", 61 "mentioned".
- 18 distinct releases named: FOMC Statement (34 members, all "All products" per F6.4), Employment
  Situation/NFP (11), CPI (8), PPI (1), ISM Services PMI (7), Crude Oil Inventories/WPSR (8), Natural
  Gas Inventories (4), API weekly bulletin (2), WASDE/Crop Production (8), USDA NASS Crop Progress
  (1), Treasury auctions (4), ECB fix (2), London 4pm fix (5), Tokyo 9:55 fix (2), LBMA gold/silver AM
  auction (2), LBMA gold PM auction (3), G.17 industrial production (3), CME CF Bitcoin Reference
  Rate/BRR final settlement (2).
- 5 of the 18 are already in Topstep F6.4 (FOMC, Unemployment Rate/Employment Situation, Crude Oil
  Inventories, Natural Gas Inventories, Crop Production); marked `in_f6_4: true`. The other 13
  (CPI, PPI, ISM Services, API bulletin, USDA Crop Progress, Treasury auctions, ECB fix, London fix,
  Tokyo fix, LBMA AM/PM auctions, G.17) are not on Topstep's table and are `in_f6_4: false`.

## Flags for the lead (not decided here)

- **Fix vs. release.** K3-tkypre-01's own text says explicitly: "the fix is a scheduled benchmark,
  not a release" (K3.md). K5-preauc-01's Topstep-check item 7 raises "should the lead count auction
  starts as releases" as an open question. The ECB fix, London 4pm fix, Tokyo fix, and LBMA AM/PM
  gold/silver auctions are benchmark-setting windows, not macroeconomic data releases; whether D8's
  "scheduled major release" language covers them is a lead decision, not made here.
- **CPI vs. Employment Situation conflation.** Several members' text uses "the 07:30 releases" or
  "Employment Situation or CPI" generically for the same 07:30 CT BLS slot without saying which
  release fell on that date. I recorded both release names separately where the passage names both
  (e.g. K5-ml-01 KF4, K7-ml-01 KF1, K8-flight-01); where a passage says only "the 07:30 releases" or
  "07:30 BLS release" with no further specificity (K2-cp3-01, K3-cp3-01, K3-ecbfix-01, K5-cp3-01,
  K5-ovr-01, K7-expiry-01), I filed it under "Employment Situation / Unemployment Rate release
  (NFP)" since that is Topstep F6.4's named 07:30 release, and noted the generic wording in `note`.
  The lead should decide whether these ambiguous mentions should instead map to a combined
  "07:30 CT BLS release" calendar entry rather than being folded into NFP specifically.
- **G.17 mapping.** K5-cp2-01's guard list gives "08:15-08:16" with no name; K5-cp3-01 and K5-ovr-01
  independently name that same clock time "G.17 (copper)". I mapped all three to G.17 on that basis
  — a light inference, flagged here rather than treated as fact.

## Unfinished / not done

- Nothing left unfinished within scope. Did not attempt to judge which releases are "major" or
  belong on the D8/D9.12 calendar (lead's call, per brief).
- Did not extract release mentions from `reports/stage_e0_catalog_K1.md` .. `_K8.md` sections other
  than "## 1. Members" (Excluded members, Beyond budget, Routed to K8, Log accounting, Trial count
  table, Questions for the lead) since those are not catalog members. If the lead wants the X-item
  candidates' named releases too (e.g. K5 log's GDP, durable goods, industrial-production mentions
  in section 2), that is a separate, larger pull not in this brief's scope.
