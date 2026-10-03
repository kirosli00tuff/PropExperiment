# MarginFetch log, Stage E.12 Task 2a

Worker MarginFetch-OpusHigh, 2026-10-03 08:07-08:25 PDT. Times below are UTC (PDT = UTC-7). Files are under
reports/stage_e12_briefs/margin_pages/. sha256 is of the bytes as saved (gzip bytes for .gz; the decompressed .csv
next to each .gz is what the JSON cites, and its own sha256 is in the JSON).

## Route decisions

- WebFetch on the CME margins page timed out. A plain GET returned HTTP 403 with CME's statement that the IP is blocked
  for suspected scraping and that scripts, robots and other scraping tools are prohibited under its Data Terms of Use.
- Scrapling get, Scrapling fetch, stealthy-fetch and Firecrawl were NOT run against cmegroup.com: after that explicit block
  they would be circumvention. Terms check: the 403 body (curl_mnq_margins.html) and Terms of Use section 8 (Wayback
  capture 2026-09-27). Section 8(vi) also bars using website data with AI tools to generate output. Flagged for the lead.
- Wayback (archive.org) was used for every figure, as the stage prompt's Task 2a allows when the live page blocks.
- No WebSearch was used. No budget or cost notice was seen.

## Fetches

| UTC time | URL | route | result | file | sha256 |
|---|---|---|---|---|---|
| 2026-10-03 15:07Z | https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.margins.html | webfetch | timeout 60 s; nothing saved | - | - |
| 2026-10-03 15:08:55Z | https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.margins.html | curl plain GET (diagnostic) | HTTP 403, JSON body: IP blocked for suspected scraping; cites CME Data Terms of Use | curl_mnq_margins.html | eecde3fafbde4090c30e610a7ed4b8d877f8351c0490e4189574890e8a5a4f7e |
| 2026-10-03 15:09Z | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/CmeWS/mvc/Margins/*&from=2026 | wayback CDX | 200, 24 captures listed | cdx_cmews_margins_2026.json | 0b6a9de513a64cf2936782d00264e011276a28155f27f07443f60b870ea8d444 |
| 2026-10-03 15:09:27Z | web.archive.org/web/20260912195431id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?exchange=CME | wayback | 200 gzip; 1456 CME rows; no equity-index flagships | wb_20260912195431_outright_cme.csv.gz | 7a9ce7da38eba56de8b28184b4650cd0826021e551e18f39f1cb7b8650154b46 |
| 2026-10-03 15:09:27Z | web.archive.org/web/20260612062305id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv | wayback | 200 gzip; 6708 rows CME/CBT/NYM/CMX; no ES/NQ/RTY/YM/CL/MCL/NG | wb_20260612062305_outright_all.csv.gz | 0248d40ea4671e702bcdff51136cad034fdc49875f2ffa7bdd2bf6015ca1e5d5 |
| 2026-10-03 15:09:28Z | web.archive.org/web/20260905215027id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?sector=FX&exchange=CME | wayback | 200 gzip; 82 FX rows (cross-check only) | wb_20260905215027_outright_fx.csv.gz | 5a5c2fb1f513f70f6e2e3edc7fd3a377a3f4e068ce02364e14f2011c1e8d4d50 |
| 2026-10-03 15:09:28Z | web.archive.org/web/20260912194807id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?sector=EQUITY%20INDEX&exchange=CME | wayback | 200 gzip; only TRB/TRI/TRM | wb_20260912194807_outright_eq.csv.gz | 0b132eccf79a41ec4de7e5bbd6d81f68cf412c387607f71e6ce32cfdd7b2e21e |
| 2026-10-03 15:09:29Z | web.archive.org/web/20260912195047id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?sector=EQUITY%20INDEX&exchange=CME&pageNumber=2 | wayback | 200 gzip; identical to page 1 | wb_20260912195047_outright_eq_p2.csv.gz | 0b132eccf79a41ec4de7e5bbd6d81f68cf412c387607f71e6ce32cfdd7b2e21e |
| 2026-10-03 15:10:14Z | web.archive.org/web/20260612id_/...clearingCode=NQ|RTY|YM (date-only ts) | wayback | 302 redirect, nothing kept; refetched with exact ts | - | - |
| 2026-10-03 15:10:16Z | web.archive.org/web/20260812081432id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT?...clearingCode=MOX... | wayback | 200; format check only | wb_20260812_json_MOX.json | 1db3cc30f67159d893bb74c008edb980c4d67ce2a0984e88cc82184449fa7dc8 |
| 2026-10-03 15:10:16Z | web.archive.org/web/20260324000209id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT?...clearingCode=GC... | wayback | 200; GC March capture, not used (June CSV newer) | wb_20260324_json_GC.json | de3705f545478936030621c218fb00864eda29af233b00e0ae0f5cd265aead6c |
| 2026-10-03 15:10:23Z | web.archive.org/web/20260612200939id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT?...clearingCode=NQ&sector=EQUITY%20INDEX... | wayback | 200; total 0, empty | wb_20260612200939_json_NQ.json | b696be0e9cb6c98344a01b4ff5ecc730b143b638fee8f8a7db0657661614541c |
| 2026-10-03 15:10:24Z | web.archive.org/web/20260612201024id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT?...clearingCode=RTY... | wayback | 200; total 0, empty | wb_20260612201024_json_RTY.json | b696be0e9cb6c98344a01b4ff5ecc730b143b638fee8f8a7db0657661614541c |
| 2026-10-03 15:10:24Z | web.archive.org/web/20260612201043id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT?...clearingCode=YM... | wayback | 200; total 0, empty | wb_20260612201043_json_YM.json | b696be0e9cb6c98344a01b4ff5ecc730b143b638fee8f8a7db0657661614541c |
| 2026-10-03 15:10:30Z | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/notices/clearing/2026/* | wayback CDX | 200; last captured notice 26-266 (Aug 2026) | cdx_clearing_notices_2026.json | 8efea4904777ec7d442ff95dd0ba4cb57f3a30b88bba911ce92de0a82f48767b |
| 2026-10-03 15:16:50Z | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/content/dam/cmegroup/notices/clearing/2026/* | wayback CDX | 200; 35 advisory PDF captures, latest chadv26-266 | cdx_dam_notices_2026.json | 06c59645f4bed0ee0c1076c25f4e443505bba2c23522f42ac073372135d6d9b6 |
| 2026-10-03 15:18:20Z | https://web.archive.org/cdx/search/cdx?url=cmegroup.com/CmeWS/mvc/Margins/*&from=2024 | wayback CDX | 200; equity JSON with data only in 2024 (ES); none for CL/MCL/NG | cdx_cmews_margins_2024on.json | e611de8d8b57adb25665bdb3c454ad13634b4458358752d751da504fc400c428 |
| 2026-10-03 15:18:40Z | web.archive.org/web/20260612200654id_/https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT?sortField=exchange&sortAsc=true&sector=EQUITY%20INDEX&exchange=CME&pageSize=50&pageNumber=1&isProtected | wayback | 200; total 3: TRB/TRI/TRM only | wb_20260612200654_json_eqsector.json | 35504400008f72b5f4c8df5101e576ad5493560b3cfc90561ce4aece02b80442 |
| 2026-10-03 15:24:01Z | web.archive.org/web/20260927062650id_/https://www.cmegroup.com/files/terms-of-use.pdf | wayback | 200; ToS section 8(vi) AI-use clause | wb_20260927062650_cme_terms_of_use.pdf | 8987ce65a4798c8cf42c8f9e511a88aa84c7174f661d22cf04b71e904685712b |

## Advisory captures (all route wayback, fetched 2026-10-03 15:11Z-15:23Z UTC)

URL pattern: https://web.archive.org/web/<ts>id_/https://www.cmegroup.com/notices/clearing/2026/MM/<n>.html and
.../content/dam/cmegroup/notices/clearing/2026/MM/<n>.pdf. Each was grepped for the 34 symbols' clearing codes and names.
Result: none of the captured 2026 advisories gives an outright rate for NQ, MNQ, RTY, M2K, YM, MYM, CL, MCL or NG.
chadv26-266 (effective after the close 2026-08-07; latest captured) changes none of the 25 quoted products.
Not retrieved after retries: 26-201.html, 26-2023.html, 26-240.html (HTTP 000 connection failures).

| file | sha256 |
|---|---|
| notices/26-171.html | ca1f42118c505812c2c736cab54a62a5e001e578a2fcad2e4c1faed4976b841f |
| notices/26-172.html | abd7473c12e1f1283d75a5d2f0a0c40c7db99decd62ece5a49ef6f4f8309c392 |
| notices/26-173.html | 49c663d3522cfc6578e6a566b144fd66514284898671f218825c84612486aed8 |
| notices/26-174.html | 4e3814d90c53e8e9eba45e34c7fe20252080b9d7073e06f827285df3e0d98cd7 |
| notices/26-176.html | d9a4b981a1529add2365f4b56db9a3705cb42ba8e53e222473340e1d23141faa |
| notices/26-177.html | 039b0d873652633fa249ddc029c54276873259df15d97e93f639bcdaef244732 |
| notices/26-178.html | 0da96d50f531485d9b42fbd72b4aeedb0005914d6164fbef18db1fffc8ba3bc6 |
| notices/26-185.html | 44c9fb3cb481741d265a81574fff49c7948fa9bd7209820fa4437ca8902d7fb4 |
| notices/26-186.html | ca469190983d77ed2ba80f5817cd3b52324db5157a413222fb656107a9579ae2 |
| notices/26-187.html | adc10051305c59fb2d1fec4ae63e355a8bd187622b2f6eb17c712647d780334d |
| notices/26-188.html | acc57cb0222957cf69febc8c21e4507bf533cd5d195b1d4f77019b54a291b804 |
| notices/26-189.html | 5964fe91c9d57b7eb6d1710dd02e38e23017219011713cf54abe15dcf3997ab2 |
| notices/26-190.html | f5893e8246e6ea478d973c11158e40e3813dafb363ea1ba392a16b3a4abc6a2f |
| notices/26-192.html | 41a071056f4ff7806784d0501aea2bb4eedf396ac28dabc33604c6c8ded352e8 |
| notices/26-193.html | 1754cfcb00babe89ffc618d8b1a8d3fdc0865ebe0fc73bf2e2a95c312ec52262 |
| notices/26-194.html | a2f1d3ee7700b4f8667c38d9523006ca6b7d01d618b3b77aebd93e5e556706bc |
| notices/26-195.html | 478349a742725fd634020b7638398a555441d1ce5a348b6a8356cc27cae1801d |
| notices/26-196.html | d615264c7fed9af479cfe13de63cfaea94e937cc14e891ac1def87f85bb54ae1 |
| notices/26-197.html | e6db62847f87a38da824be305a66f9f278506be8d7e9b348a66fbcbae645e570 |
| notices/26-198.html | b8393eacddc4911254f19e13c26e8459657a52451e061c99f5f26d72d6550d6b |
| notices/26-199.html | 3ea5bbbc22d5ccff46eee4c6a6e9ac4f8f6ef1f6576922536e7c703c94a00e44 |
| notices/26-202.html | be7311376f0a3596a4875ba649656e77f18b5d1d2f5753cc1611452328a9d5a4 |
| notices/26-220.html | 1f4a692c4e4c81759dba80b917ce6a7daf527f9ccdbd8eb3482247248580ffbe |
| notices/26-226.html | 6a2e81565e0bda9698a7b4ce577abb4a259e25f7c2a6457c32e243d6801798da |
| notices/26-245.html | 49653b3fb52afda97b014147b808e2f7cf693281cc736fe1788a0e08428bd275 |
| notices/26-248.html | 7e49a6e7922ce6bc5978f921bdc28651edadf11ccafe1716eddccd34b38e43c9 |
| notices/26-250.html | 9f1107bf015be6a2dac50b3228f243138807ffe400d2bc4cc6ba49620fc986e8 |
| notices/26-252.html | 61355b01db5a8b351fa32f6a9e888725e4b41bb8da101f5fb89cbbf04c80c309 |
| notices/26-266.html | 5c5d7583c0483318aa797690da25d89cd9e6750d77a65959f775d48ca1d34f36 |
| notices/chadv26-006.pdf | fd5a1f19c44ed47f97a085450d31d7fb5f33dead82805dbc3570b38ee7e34670 |
| notices/chadv26-015.xlsx | fd8ad0c5361d80752418e664617d8f0d570d3f5fa927f9aaca0c4eb58b337dbd |
| notices/chadv26-016.pdf | 41cdf3c9b3e59efc7e93460db06329ca511f334f864821c8676370235f54e8ab |
| notices/chadv26-019.pdf | 42c4935dd0cd78bd2a83e568a0ceefab0750019f3a795ae8aea8d77f36e3bdbc |
| notices/chadv26-022r.pdf | cc2e077aacf17b346ac949e7e7e8260018a11a89a238f5d96bb39e62f6d13b8f |
| notices/chadv26-023r.pdf | 3470bde738ef6ff0d64dd528a647877c93daa60e6b90b216ff7e5ac766308d0a |
| notices/chadv26-027.pdf | caa75dce47b0d6eec5755c30920b5ba48ceb2cade7a1952acbe37fde91bd554b |
| notices/chadv26-035.pdf | 25dc5268ec4ed55334e0304650721970cd8c69021a78a505cb3d642a8c1afa1d |
| notices/chadv26-038.pdf | 3c79bdb09ca8be51661c035c863bf0cc7a42da6f1bdaac40a8053625ce51288f |
| notices/chadv26-041.pdf | 1d0062ae036146c1f3afe912102a5e7642997ac00d494cafa3a11df3cfcab95b |
| notices/chadv26-057.pdf | abacfb93f529cc12fc9fb37b4afcd5adfe611bc651b7bbf18b1c80e070bad123 |
| notices/chadv26-066.pdf | 30ddc5025680a383ece9faaf8c0cc9c5d9380353ae28a48339583174fcdd1919 |
| notices/chadv26-078-1.pdf | 324fc08a60218adffcad0b43702179316a30024da443e542f0ae0dea4a8bce18 |
| notices/chadv26-084.pdf | b67027f4c78cede75240dee5f4f6d52f9521121d3e898baa0e4bfe435d3f1715 |
| notices/chadv26-095.pdf | 398d062cca97991dad15c773f18e4b110c1689606ee44230cc91c9bd4d4cf788 |
| notices/chadv26-139.pdf | 38dadb8da95a52d3dce74e0b04fbef677ac4b81a883330df447198ac099ffd27 |
| notices/chadv26-148r-1.pdf | 6c205698f8a5102e57ccb80d1cc860f228dfed9ca57ceb0c8c0c7565c4680796 |
| notices/chadv26-152.pdf | 735277904bec66739f59664017712dcf69a24639438bd0c41122522e56f97cc7 |
| notices/chadv26-157.pdf | c7491950f1ce031d2b7ede2d72d492c160cca4caa5796afddb2d9e516de7eec2 |
| notices/chadv26-162.pdf | 71f8eeefafad65ab54b2087868df8132800a55afd336a7d88a86ba8bf45c80ff |
| notices/chadv26-198.pdf | 63d68dca238536fe9bad60e92db043adb84770ead797c482b757c3a11f879d2b |
| notices/chadv26-220.pdf | 1543303614e55f6f9a6bf0daeab352359aebe534ec5da57335d682a0d632fe67 |
| notices/chadv26-226.pdf | 6481f88f243aed78b50a3866c28b48795b3987e8b05fc0dba92c710773399547 |
| notices/chadv26-240.pdf | a2095cfa130fa53fc35401793e75e24d2226bcdcdb82a46d6726b8ee73725517 |
| notices/chadv26-245.pdf | 5ce74fbca9ef74cfe44d9c6fa14dd8bf8a9e67c82efee7bbd5f11b03a14de62a |
| notices/chadv26-248.pdf | 8b56f51e24a97e9a9bdc5cd2559f7a2b64071a1b89948b8a44afa42c08da0f77 |
| notices/chadv26-250.pdf | d369a54038543f26d0fd461459b2a1e5ab9402b557a732553ecf4c2d0686d1e3 |
| notices/chadv26-252.pdf | c6028d3027eaf7db4405bef93bfb1e34602e064e7d3779ae44d53b26dc4a275a |
| notices/chadv26-266.pdf | 73be8494b97723968b895d8e5616ef52aa14ec0e7356095889d2724c65496c8c |
| notices/chasv26-153.pdf | aec4082d6e53b8d57ae9f43f3120e70bbf75a262fac6d06ce7f1f7a92de3b0d0 |

notices/*.txt are pdftotext conversions of the PDFs, used for grep only.
