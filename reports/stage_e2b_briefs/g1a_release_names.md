# Brief: ReleaseNamesExtractor-SonnetMed (worker-medium on sonnet) - complex extraction, no conclusions

Objective: list every scheduled release, report, statement or announcement that any member of the frozen Stage E catalog
names, with the member, its products and the verbatim words, so the lead can decide which releases join the calendar
(D8: "plus the releases the product's catalog members name").

Read reports/stage_e2b_briefs/00_common.md and reports/stage_e2b_briefs/g1_release_common.md (context only; you do no web
work). Input (read-only, frozen): reports/stage_e0_catalog.json and reports/stage_e0_catalog_K1.md .. _K8.md; also
reports/stage_e2a_source_window_amendment.md is NOT needed. Read by section (grep for words such as release, report,
announcement, statement, FOMC, CPI, payroll, NFP, employment, EIA, inventor, storage, USDA, WASDE, crop, cattle, hogs,
auction, Treasury, ECB, BoE, BoJ, RBA, RBNZ, SNB, BoC, rate decision, minutes, GDP, PMI, ISM, retail sales, PPI, PCE,
jobless, claims, OPEC, settlement, fix, and read the surrounding member entry).

Output reports/stage_e2b_release_names.json:
{"members": [{"member_id", "cluster", "traded_products": [...], "read_products": [...], "release_name_verbatim",
"quote" (the catalog sentence, verbatim), "source_file", "line", "role" ("signal" if the member's rule times on it,
"mentioned" otherwise, with the quote showing why)}],
 "distinct_releases": [{"name", "members": [...], "products": [...]}], "counts": {...}}
Also a short .md table. Include releases already in F6.4 (they still count) and mark them "in_f6_4": true. No judgment
about whether a release is "major": list everything named. Report: reports/stage_e2b_release_names_worker.md with counts
and the grep terms used. Reply with the path, a summary of at most 150 words, and anything unfinished.
