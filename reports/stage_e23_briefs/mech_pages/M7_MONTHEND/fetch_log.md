# M7_MONTHEND fetch log

| URL | fetch time (PDT) | saved file | sha256 | tool | note |
|---|---|---|---|---|---|
| https://acris.aalto.fi/ws/portalfiles/portal/40965155/hhz054.pdf | 2026-10-17T02:18:27-07:00 | etula_etal_2020_rfs_dashforcash.pdf | 7f66ea4a5aa2b9285fc210f6cd0c73924ede5bd4ff5d788d369f390b1b9939f4 | curl (HTTP 200) | PDF document, version 1.5, 10 page(s) (z RFS published CC BY |
| https://repec.cepr.org/repec/cpr/ceprdp/DP15617.pdf | 2026-10-17T02:18:29-07:00 | camanho_hau_rey_cepr_dp15617.pdf | 963c26c24d2f400f653840760860d2272964d229ee65fd83bd84c5438884655e | curl (HTTP 403) | HTML document, ASCII text, with very lon CEPR DP Dec 2021  403 blocked, file removed |
| https://www.cxoadvisory.com/bonds/term-premium-end-of-month-effect/ | 2026-10-17T02:18:30-07:00 | cxo_hs_review.html | 28f2ee845f5c9e61d7e7d600832d24e95681643f92b6ba8bbb9b877f875daf76 | curl (HTTP 200) | HTML document, ASCII text, with very lon secondary review |
| https://www.nber.org/system/files/working_papers/w24320/revisions/w24320.rev1.pdf | 2026-10-17T02:18:37-07:00 | camanho_hau_rey_nber_w24320rev1.pdf | 7a7f011f2ccc6efc1f09c1c70ce19be3540a73a45162074db56eb6aee4890f0a | curl (HTTP 200) | PDF document, version 1.6 (zip deflate e NBER WP rev Dec 2020 |
| https://ideas.repec.org/a/eee/riibaf/v24y2010i1p75-81.html | 2026-10-17T02:19:52-07:00 | ideas_jalonen_etal_2010_riibaf.html | 6dd806eb4fd3780cc47c64cdaa34b8770a975d6160edd9d16ab6bdc26d814b7a | curl (HTTP 200) | HTML document, Unicode text, UTF-8 text, abstract page |
| https://beyondpassive.substack.com/p/two-calendar-effects-at-the-month | 2026-10-17T02:19:54-07:00 | beyondpassive_month_boundary.html | 34f7bfc9081ff0d5f10d9cf747d4c50d7636e3ae5e41bd2070f919e1fca78130 | curl (HTTP 200) | HTML document, Unicode text, UTF-8 text, blog, secondary |
| https://www.edhec.edu/sites/default/files/2026-03/slides_EDHEC_Michele%20Mazzoleni%20%281%29.pdf | 2026-10-17T02:20:45-07:00 | hmm_rebalancing_edhec_slides.pdf | c21b1a0fd14b8e8c3a1a8e00b29c68c97bd99b79c4b154e09bddd9ce49843a8a | curl (HTTP 200) | PDF document, version 1.5, 6 page(s) slides, Harvey-Mazzoleni-Melone |
| https://bfi.uchicago.edu/wp-content/uploads/2020/11/Liao_The-Hedging-Channel-of-Exchange-Rate.pdf | 2026-10-17T02:21:18-07:00 | liao_zhang_hedging_channel_bfi2020.pdf | 25770dd5d396f9c26f41c755caf072ee0d9523712609d7307670b51f854becbb | curl (HTTP 200) | PDF document, version 1.5 (zip deflate e BFI WP version |

Notes:
- CEPR DP15617 returned HTTP 403 (02:18:29 PDT); the 403 body was deleted and the NBER w24320 rev1 PDF used instead.
- cxo_hs_review.html (secondary review of Hartley-Schwarz) was saved but not used as evidence.
- liao_zhang_hedging_channel_bfi2020.pdf: grep found no month-end content; not used as evidence.
- PDFs were converted with `pdftotext -layout` to <file>.txt; HTML pages were stripped to <file>.txt by a one-line python call. Reads were by grep and line ranges.

Reused pages saved by Stage E.20 (not refetched; fetch metadata in reports/stage_e20_briefs/pages/6E/fetch_log.tsv and the E.20 ZN notes):
| saved path | sha256 |
|---|---|
| reports/stage_e20_briefs/pages/ZN/hartley_schwarz_2019.pdf (.txt) | 56403762378f606f595dcce11afcf1f1eaccf8810237c58999f653a230a32809 |
| reports/stage_e20_briefs/pages/6E/melvin_prins_2013_ecb_wp.pdf (.txt) | 606a6c402741982f4f81423f6df3ca055348156fe728d54976807579168d587c |
| reports/stage_e20_briefs/pages/6E/krohn_mueller_whelan_2024_jf_wrap.pdf (.txt) | a7975f26f9b42b837a0b2a6c1474a63e448fff5a0fa7957bc2233b1c0302e6a3 |
| reports/stage_e20_briefs/pages/ZN/lse_index_strike.html (.txt) | 2036a2f067b9c0639d01ede8cb3dd0991f57dd0dea5874cdd06819c6c2336553 |
