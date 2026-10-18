# Alpaca reader log (Stage E.24, AlpacaReader-OpusHigh)

Session window: 2026-10-18 01:35 to about 01:50 PDT (from `date`). All fetch times below are UTC as recorded by the fetch script at save time.

## Method

- Fetcher: `reports/stage_e24_briefs/scripts/alpaca/fetch.sh` (curl GET with browser UA, 2 s sleep before each request; scrapling `extract get` fallback on non-200 or empty body; never needed). Every saved file is under `reports/stage_e24_briefs/pages/alpaca/`; the raw log is `scripts/alpaca/fetch_log.tsv`.
- Deviation from the brief's fetch order: WebFetch was not used for evidence pages, because WebFetch returns a model summary and cannot save the raw page the brief requires. A plain curl GET (the same request WebFetch makes) was used instead and the raw bytes saved. No page failed, so no Scrapling or Firecrawl fallback was used.
- docs.alpaca.markets is a ReadMe site that serves each page as Markdown when `.md` is appended; the `.md` variant was saved (it is the vendor's own source text, including OpenAPI JSON on reference pages). `docs_*.md` files are from `https://docs.alpaca.markets/docs/<page>.md`; `docs_us_*.md` and `ref_us_*.md` from `https://docs.alpaca.markets/us/docs/<page>.md` and `/us/reference/<page>.md`. `docs_paper-trading.md` was compared byte-for-byte with the `/us/docs/paper-trading.md` copy (one unsaved curl GET at about 08:44Z) and is identical.
- Derived files (not fetched): `alpaca_TermsAndConditions.pdf.txt` (pdftotext of the saved PDF); `alpaca_py_0.44.0/src/` (unzip of the saved wheel; read by grep only, never imported or executed).
- Pages read by grep / line ranges / short python field extractors only.

## Terms and robots (read before content fetches)

- docs.alpaca.markets/robots.txt (08:35:51Z): `User-agent: * / Allow: /` with disallows only for `/*/api-next`, `/cdn-cgi/`, `/edit/`, `/suggested-edits/`, `/login`, `/logout`; it advertises `https://docs.alpaca.markets/llms.txt` for LLM agents. Docs fetches are allowed.
- alpaca.markets/robots.txt (08:35:54Z): no robots file; the server answers HTTP 200 with its 404 HTML page (81,029 bytes). No crawl restriction published.
- Alpaca Terms and Conditions PDF (files.alpaca.markets/disclosures/library/TermsAndConditions.pdf, linked from alpaca.markets/disclosures; 08:36:15Z): no clause on robots, scraping or automated access (grep for robot|spider|scrap|automat|crawl|harvest: no hits in this sense). Relevant clauses: "you agree to use the Services and Content solely for your own personal and non-commercial purposes" and "No part of the Service or Content may be copied, reproduced, republished ... or distributed in any way (including “mirroring”) to any other computer, server, web site or other medium for publication or distribution or for any commercial enterprise, without Alpaca’s express prior written consent." Reading: private, non-published local copies for internal research are within personal use; the saved pages must not be republished. The pages folder should stay out of any public mirror.
- forum.alpaca.markets/robots.txt (08:42:04Z) allows topic pages, but the forum ToS (forum.alpaca.markets/tos, 08:42:06Z) says: "You may not automate access to the forum, or monitor the forum, such as with a web crawler, browser plug-in or add-on, or other computer program that is not a web browser." Therefore NO forum topic page was fetched (not by curl, Scrapling, WebFetch or Firecrawl). Forum facts appear only as WebSearch snippets and are marked [unverified, forum, not fetched]. (The robots and ToS pages themselves were fetched once each to read the rules.)
- pypi.org JSON API and files.pythonhosted.org: public package index; the 0.44.0 wheel's sha256 equals the PyPI-published digest b54673f967c0c814a5e0223cbb0211a5d9d75a8d107e792872b14e5bae957c03.
- web.archive.org: one `id_` capture fetched (redirected to capture 20241114115907) for a deprecated Alpaca page that now returns 404.

## Fetches

| # | UTC time | URL | saved file | method | HTTP | bytes | sha256 |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-18T08:35:51Z | https://docs.alpaca.markets/robots.txt | docs_robots.txt | curl | 200 | 219 | 2042117d0c08ccd4201420c7e1808a2984afb6e6417cd70f5fae75d9355cc4f1 |
| 2 | 2026-10-18T08:35:54Z | https://alpaca.markets/robots.txt | alpaca_robots.txt | curl | 200 | 81029 | e4df6a313c739c4fb9e3c2435d6951281a1030ea5c8079d42aee8b783f617f2d |
| 3 | 2026-10-18T08:36:02Z | https://docs.alpaca.markets/llms.txt | docs_llms.txt | curl | 200 | 152632 | 115ef71d414e82abc32abc4ccf3d8f6102ead259b41ad38499e4079b7235c639 |
| 4 | 2026-10-18T08:36:04Z | https://alpaca.markets/disclosures | alpaca_disclosures.html | curl | 200 | 114294 | 19d4b8c7b0a1e20f5def9bd9c79e06a8fa3697afe60f7cf8bc44d48a4dcd1e7a |
| 5 | 2026-10-18T08:36:15Z | https://files.alpaca.markets/disclosures/library/TermsAndConditions.pdf | alpaca_TermsAndConditions.pdf | curl | 200 | 27092 | 2dc774d4aeeafbe4c7f0565e7842d932bc8bc10488af805fce43b8734e7b9859 |
| 6 | 2026-10-18T08:36:39Z | https://docs.alpaca.markets/docs/paper-trading.md | docs_paper-trading.md | curl | 200 | 6260 | d43c9e2bdc1c4c9be8296a2a0b7b012441e6d293a44ea0d5c767d56d9709ade7 |
| 7 | 2026-10-18T08:36:41Z | https://docs.alpaca.markets/docs/about-market-data-api.md | docs_about-market-data-api.md | curl | 200 | 7924 | ff3f8537b88c7e2640fc6f60ed0143a7441c9f503e23c1da8c889f04c9b9362f |
| 8 | 2026-10-18T08:36:43Z | https://docs.alpaca.markets/docs/historical-stock-data-1.md | docs_historical-stock-data-1.md | curl | 200 | 2765 | f5c481f99797985246a69fc2938871ee2e2820b8ff106b20b1e0493d7a985fad |
| 9 | 2026-10-18T08:36:46Z | https://docs.alpaca.markets/docs/market-data-faq.md | docs_market-data-faq.md | curl | 200 | 34729 | b6d9225409d2211b60cfeed72e8716fc1e05f2d7593ffed6dc120a0b5ebaef13 |
| 10 | 2026-10-18T08:36:52Z | https://docs.alpaca.markets/us/llms.txt | docs_us_llms.txt | curl | 200 | 81867 | 06f585fe09c629e5baed612ead0945e7d9750d11bf21c1ad726c879a9cdcf79f |
| 11 | 2026-10-18T08:37:08Z | https://docs.alpaca.markets/us/docs/getting-started-with-trading-api.md | docs_us_getting-started-with-trading-api.md | curl | 200 | 1181 | 6c76122b9a09f53ece758591b5ccd9e8be6e9516700ac69195e0e106d494a2f3 |
| 12 | 2026-10-18T08:37:10Z | https://docs.alpaca.markets/us/docs/working-with-account.md | docs_us_working-with-account.md | curl | 200 | 4269 | ceedd86532c528ed9199beaab66cb0f3a77342baf90afda37452201e75bdfcf1 |
| 13 | 2026-10-18T08:37:13Z | https://docs.alpaca.markets/us/docs/working-with-orders.md | docs_us_working-with-orders.md | curl | 200 | 22976 | d75d5018099ecf88e688fd5b7861f3f8a0d81eb2844afdbc049c0c4aefcc297f |
| 14 | 2026-10-18T08:37:15Z | https://docs.alpaca.markets/us/docs/account-plans.md | docs_us_account-plans.md | curl | 200 | 10885 | d69313e856e1d55c7e27237730fa3314b36dc2afc0b8763e57319af4ad5adc3a |
| 15 | 2026-10-18T08:37:18Z | https://docs.alpaca.markets/us/docs/fractional-trading.md | docs_us_fractional-trading.md | curl | 200 | 4467 | 218dc0b259d2684fa053dbf1a5736c36cca1abbc1df343571bb6c407df4fc3be |
| 16 | 2026-10-18T08:37:20Z | https://docs.alpaca.markets/us/docs/margin-and-short-selling.md | docs_us_margin-and-short-selling.md | curl | 200 | 12916 | 1a8bd0e5f12485e46881b08c2074c38d7a41af2a0bc81736fa693e2ed0be1ff7 |
| 17 | 2026-10-18T08:37:22Z | https://docs.alpaca.markets/us/docs/orders-at-alpaca.md | docs_us_orders-at-alpaca.md | curl | 200 | 65454 | e35915bdf3da6ebfc5dd76cc6ed5cbed078f27e169022f9489a31d4e8e7c890b |
| 18 | 2026-10-18T08:37:24Z | https://docs.alpaca.markets/us/docs/user-protection.md | docs_us_user-protection.md | curl | 200 | 6536 | 02a0f7b6b00a8b6f459c4e5b3f25b7fbf065011fbde2985bed860791d3a5765e |
| 19 | 2026-10-18T08:37:27Z | https://docs.alpaca.markets/us/docs/understanding-the-new-intraday-margin-rule.md | docs_us_understanding-the-new-intraday-margin-rule.md | curl | 200 | 3367 | 34e04c55e961964e990a2d38a88d31257c3a3d3c914f9bedf450be1438ec2db9 |
| 20 | 2026-10-18T08:37:29Z | https://docs.alpaca.markets/us/docs/the-intraday-margin-rule.md | docs_us_the-intraday-margin-rule.md | curl | 200 | 4776 | 03e8fc0dd722bf54b7928cc6ca584bb6f9057ff0b8a8a361297f600c0092713a |
| 21 | 2026-10-18T08:37:31Z | https://docs.alpaca.markets/us/docs/getting-started-with-alpaca-market-data.md | docs_us_getting-started-with-alpaca-market-data.md | curl | 200 | 9944 | ccde972295c02b5bce84def1a78ba6f1a3d161f95ee4c2e3f47b24f0e018fc04 |
| 22 | 2026-10-18T08:37:33Z | https://docs.alpaca.markets/us/docs/historical-api.md | docs_us_historical-api.md | curl | 200 | 925 | 6c9930d4efffc52c863ff004e8d81ca59b2a7890dc77f9374b8da142e02a7399 |
| 23 | 2026-10-18T08:37:35Z | https://docs.alpaca.markets/us/docs/authentication.md | docs_us_authentication.md | curl | 200 | 4042 | 9043fc418434c49a3091a196df8b052ad5deac83176420d457c0786ad7150321 |
| 24 | 2026-10-18T08:37:38Z | https://docs.alpaca.markets/us/docs/sdks-and-tools.md | docs_us_sdks-and-tools.md | curl | 200 | 3639 | 8a3f45fa690199c804f172ee3b35f31832aee0d458d4c9ff353a388860222454 |
| 25 | 2026-10-18T08:37:40Z | https://docs.alpaca.markets/us/docs/trading-api.md | docs_us_trading-api.md | curl | 200 | 1827 | 3e519fdb7e7f7cee169d58e3622f581aaec6289614a1fd08ed33a543f2898b41 |
| 26 | 2026-10-18T08:37:46Z | https://docs.alpaca.markets/us/docs/understanding-finras-new-intraday-margin-rule-and-the-end-of-pdt.md | docs_us_finra_intraday_margin_end_of_pdt.md | curl | 200 | 9190 | 3152b6fb87598844aa195570d708cc91b45c29a82df00227524ad8c61ecd6145 |
| 27 | 2026-10-18T08:37:49Z | https://docs.alpaca.markets/us/reference/getaccount-1.md | ref_us_getaccount-1.md | curl | 200 | 13654 | df64d8b98715d2fd0667fec4cefa4f8507cb2025a49e3c5fdf471bf938ec9c91 |
| 28 | 2026-10-18T08:37:52Z | https://docs.alpaca.markets/us/reference/postorder.md | ref_us_postorder.md | curl | 200 | 51112 | 913d6f80c0f1bbedb3f34f0d70f1c2e45c55599ec971b7fed938a2785a287463 |
| 29 | 2026-10-18T08:37:54Z | https://docs.alpaca.markets/us/reference/stockbars.md | ref_us_stockbars.md | curl | 200 | 17585 | ce83070b28337c8e9cdaf7d734ff4fd91d23e0bc6b1979548e63de9fdfe7f722 |
| 30 | 2026-10-18T08:37:57Z | https://docs.alpaca.markets/us/reference/corporateactions-1.md | ref_us_corporateactions-1.md | curl | 200 | 47620 | b3c31fadd5a7ae89f8c0e4bd7d575bc5180faceda69ea1f115b4c1710d835803 |
| 31 | 2026-10-18T08:39:24Z | https://docs.alpaca.markets/us/reference/stockauctions-1.md | ref_us_stockauctions-1.md | curl | 200 | 21702 | 8a6e8687094bbcb554805ede303a28743638e23b607bca311b2068d1691f56d2 |
| 32 | 2026-10-18T08:41:35Z | https://docs.alpaca.markets/us/docs/broker-api-rate-limits.md | docs_us_broker-api-rate-limits.md | curl | 200 | 4792 | b757a249b6684117849a23af06da484eae6004c07eae9357235c60f2535667f3 |
| 33 | 2026-10-18T08:41:38Z | https://docs.alpaca.markets/us/docs/getting-started.md | docs_us_getting-started.md | curl | 200 | 1625 | 350e9f093cdddc84e7c8e36f5eebb2acc4f8997ec3fa67eeaa02ac34cd1b0c47 |
| 34 | 2026-10-18T08:42:04Z | https://forum.alpaca.markets/robots.txt | forum_robots.txt | curl | 200 | 1001 | eb53a98992f60c56c70f8e3f64cfae840b02a1ccc849cc4a181cdfa154d39d18 |
| 35 | 2026-10-18T08:42:06Z | https://forum.alpaca.markets/tos | forum_tos.html | curl | 200 | 155529 | d118294ed84ddc7b4cac2f61a73e477c66f6d95ae445a586a50255816491fcda |
| 36 | 2026-10-18T08:42:27Z | https://alpaca.markets/deprecated/docs/api-documentation/api-v2/ | alpaca_deprecated_api-v2.html | curl | 200 | 81029 | e4df6a313c739c4fb9e3c2435d6951281a1030ea5c8079d42aee8b783f617f2d |
| 37 | 2026-10-18T08:42:29Z | https://pypi.org/pypi/alpaca-py/json | pypi_alpaca-py.json | curl | 200 | 165355 | 307ab2dec1484d06935a61f7a08ee302a51f12e0e560b13ec8491ede623e9a20 |
| 38 | 2026-10-18T08:42:49Z | https://web.archive.org/web/2023id_/https://alpaca.markets/deprecated/docs/api-documentation/api-v2/ | wayback_alpaca_deprecated_api-v2.html | curl | 200 | 56473 | 4b8d28cb9c6db4ca0a7efb775b0e182165c34247d7364010d429e8b5f59a3513 |
| 39 | 2026-10-18T08:43:09Z | https://files.pythonhosted.org/packages/8e/9e/69a2d867988578d6f9e52e35d435d8a43296257cf590fb881a3752de7651/alpaca_py-0.44.0-py3-none-any.whl | alpaca_py_0.44.0/alpaca_py-0.44.0-py3-none-any.whl | curl | 200 | 128904 | b54673f967c0c814a5e0223cbb0211a5d9d75a8d107e792872b14e5bae957c03 |

## Failures and notes

- #36 `alpaca_deprecated_api-v2.html`: https://alpaca.markets/deprecated/docs/api-documentation/api-v2/ returned HTTP 200 with the site's 404 page (same sha256 as #2). The file was then deleted as a non-evidence 404 page (its hash stays in this log). Replaced by the Wayback capture #38 (capture time 2024-11-14 11:59:07 UTC, from the 302 Location header of a HEAD request).
- #2 alpaca.markets/robots.txt: same 404 page; kept as evidence that no robots file exists.
- `gh search code` for the rate-limit text failed (HTTP 401, gh not authenticated); not retried.
- The trading-API rate limit is not stated on any current docs.alpaca.markets page found; the only vendor text is the deprecated v2 page via Wayback (#38).

## WebSearch use

- About 01:41-01:45 PDT (bracketed by fetch-log times, not separately timestamped): 4 WebSearch calls (trading API rate limit; dividend adjustment method x2; paper MOC fills). No over-budget notice was received. Results pointed mostly to forum.alpaca.markets threads, which the forum ToS bars from automated fetching, so they were not fetched; snippets are cited as [unverified, forum].
- No Firecrawl call was made. No broker or data API endpoint was called; no account, key or credential was used or read.
