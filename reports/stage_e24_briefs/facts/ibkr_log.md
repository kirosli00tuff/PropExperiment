# IBKR fact reader log (IBKRReader-OpusHigh, Stage E.24)

Worker started 2026-10-18 01:35 PDT (`date`), log written 01:5x PDT. Every time in the fetch table is UTC, as the
brief asks; PDT = UTC - 7 h. No broker or data endpoint was called, no account was opened, no API key was used or read.

## Method and deviations

- Fetch tool: `scrapling extract get <url> <file>` through the private script `scripts/ibkr/fetch.sh`. That script logs
  the UTC time, return code, byte count, sha256 and URL to `scripts/ibkr/fetches.tsv`, and writes a `.txt` copy of every
  `.html` file (`scripts/ibkr/h2t.py`) for grep. Pages built in JavaScript (ibkrguides.com) went through
  `scrapling extract fetch --network-idle --wait 3000|4000` (`scripts/ibkr/rf.sh`).
- Deviation from the brief's fetch order: WebFetch was not used as the first step. It returns a page summarised by a model,
  not the raw page, so it cannot meet the "saved raw" rule. I went straight to step 2 (scrapling get), then step 3
  (scrapling fetch) where the page needed a browser. Firecrawl was not used.
- `.md` files from interactivebrokers.com/docs/... come from the site's own Markdown endpoint (append `.md`; the pages
  themselves say "For clean Markdown of any page, append .md to the page URL"). Scrapling saved them through its .md writer.
  Plain-text files (IBC config.ini, gatewaystart.sh, ib_async .py source) were saved with a `.txt` extension, because
  scrapling will not write to `.ini` or `.sh` (rows 84-85 failed with rc=1, and rows 87-88 refetched them as .txt).
- Spacing: 2-7 s between requests to the same host, and at least 4 s on ibkrguides.com (its robots.txt asks for Crawl-Delay: 3).
- WebSearch: 7 standard queries were used to find official URLs. No over-budget notice appeared. Search summaries are not
  cited as evidence. Every fact comes from a saved page.

## Terms and robots read before automated fetching

| Site | What was read | What it allows |
|---|---|---|
| www.interactivebrokers.com | robots.txt (row 1); copyright notice in ibkr_homepage_disclosures.html (row 10) | robots disallows only /smf/, /fluxbb/, /insights/ibtr_alerts.php, /search/, /referral/. Notice: "Copies of the contents may be viewed and downloaded for your own personal non-commercial use, provided that any copy contains this Copyright/Disclaimer Notice." The saved raw pages keep the site footer. Use: a handful of pages for private research. No separate "website terms of use" page was found in the homepage footer links. |
| www.ibkrguides.com | robots.txt (row 5) | `User-agent: * / Crawl-Delay: 3`, nothing disallowed. Spacing was kept at 4 s or more. Same IBKR copyright notice applies. |
| interactivebrokers.github.io (legacy, deprecated TWS API docs) | robots.txt (row 2): empty, none served | Nothing disallowed. GitHub Pages content falls under GitHub's terms (below). |
| github.com | robots.txt (row 3); GitHub Terms of Service (row 7); Acceptable Use Policies (row 8) | robots disallows /*/raw/, /*/tree/, /*/archive/ and similar, and allows release pages. AUP: "Researchers may use public, non-personal information from the Service for research purposes, only if any publications resulting from that research are open access." Fetched from github.com: only the IBC releases/latest page. |
| raw.githubusercontent.com | robots.txt (row 6): 404 page, none served | No restriction found. Fetched: the IBC and ib_async source and docs files. |
| ib-api-reloaded.github.io (ib_async docs) | robots.txt (row 4): GitHub Pages 404, none served | No restriction found. |
| forum.ninjatrader.com (third party) | robots.txt (row 81) | Disallows /admin/, /auth/, /session and similar for `*`. The one thread fetched came back as a JS shell and is not used. |
| pypi.org | (not read; the single fetch hit a client challenge) | Not used. |

## Failures and non-survivors

- ibkrcampus.com/docs/llms.txt: HTTP 403 (row 39). The same index came from www.interactivebrokers.com/docs/llms.txt (row 40).
- docs/tws-api/doc/notes-limitations/limitations/paper-trading.md: "Page Not Found" (row 59). The page was removed from the current docs.
- interactivebrokers.github.io/tws-api/paper_trading.html: 404 (row 74).
- www.interactivebrokers.com/en/trading/products-exchanges.php (product search) is a JavaScript app (row 101 redirected there).
  I did not call its JSON backend: that would be a broker data endpoint, which the brief rules out. The futures margin
  table (row 104) was used for exchange, symbol and trading-class facts instead.
- margin-futures-fops.php without query string redirected to the general margin page (row 102). The `?hm=us&ex=us...`
  URL (row 104) served the full US table.
- general/market-data-subscriptions/compliance-requirements-for-api-market-data/market-data-api-acknowledgement.md: scrapling rc=1, empty (row 54). Not retried.
- ibkrguides KB 1719: the plain get and the first browser fetch returned the JS shell (rows 56-57). The browser fetch with network-idle plus a 4 s wait succeeded (row 58).
- NinjaTrader forum thread on IB daily-bar settlement (third party): the page held no thread text (row 82). Not used. Forum claims
  that IB daily closes equal the last minute bar stay [unverified, third-party, not retrieved].
- pypi.org/pypi/ib-async/json: scrapling rc=1 (row 96). pypi.org/project/ib-async/ returned a "Client Challenge" (row 98). Not used. The ib_async
  version comes from its own docs ("Release 2.1.0.") and changelog instead.
- ib_async source files were read from the `main` branch on raw.githubusercontent.com, not from a 2.1.0 tag. Line-level details could differ from 2.1.0.

## Fetch table (every fetch, in order)

| # | UTC fetch time | method | rc | bytes | sha256 | saved file (pages/ibkr/) | URL |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-18T08:36:02Z | get | 0 | 264 | `ddb8a2205f22260fbcf6c691178a218e768fba19a7a8e8a828e81d333415a5cd` | ibkr_robots.txt | https://www.interactivebrokers.com/robots.txt |
| 2 | 2026-10-18T08:36:06Z | get | 0 | 0 | `NA` | ibgithubio_robots.txt (empty: no robots.txt served) | https://interactivebrokers.github.io/robots.txt |
| 3 | 2026-10-18T08:36:06Z | get | 0 | 14483 | `16c146f2a9b5b17420c848c2ddbeeb8330ce85357aa138a3deb298230dd98971` | github_robots.txt | https://github.com/robots.txt |
| 4 | 2026-10-18T08:36:06Z | get | 0 | 253 | `60317b99b132d51239934dd1a564aaeb2f89968633a54f2b0241c46a47aba42c` | ibasync_ghio_robots.txt | https://ib-api-reloaded.github.io/robots.txt |
| 5 | 2026-10-18T08:36:07Z | get | 0 | 70 | `41c7e32ebed2d723e55d6f9f660d250d1db0117835cc0e6aac02bae65001deb7` | ibkrguides_robots.txt | https://www.ibkrguides.com/robots.txt |
| 6 | 2026-10-18T08:36:26Z | get | 0 | 14 | `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed` | rawgh_robots.txt | https://raw.githubusercontent.com/robots.txt |
| 7 | 2026-10-18T08:36:27Z | get | 0 | 366297 | `96ab45f1c37cf7d119e9d7e6576dccd48c462b5a623b598e87c5808192d82078` | github_tos.html | https://docs.github.com/en/site-policy/github-terms/github-terms-of-service |
| 8 | 2026-10-18T08:36:37Z | get | 0 | 170968 | `c7a3c4fb976d49155169ba21a9fa4cdf182742afa7e9e6e722e2d0b6d8c3a0c4` | github_aup.html | https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies |
| 9 | 2026-10-18T08:36:40Z | get | 0 | 214137 | `3537d725f66ee09819cc95222e976d8ed1cc41bccedbb9bb909e74807bed4309` | ibkr_home.html | https://www.interactivebrokers.com/en/home.php |
| 10 | 2026-10-18T08:36:51Z | get | 0 | 174069 | `83d24c5446ee6a695f721243f73092d7f72f6dd759648f82070cd5553ba30a65` | ibkr_homepage_disclosures.html | https://www.interactivebrokers.com/en/general/homepage-disclosures.php |
| 11 | 2026-10-18T08:36:58Z | get | 0 | 234129 | `f26b2a4797372f1711b399a113058607f88edadcea7eaad4b14ff519d4a557ce` | twsapi_doc.html (nav shell only) | https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/ |
| 12 | 2026-10-18T08:37:11Z | fetch | 0 | 249713 | `6e0dad156aaa26340ff734d336ede19296293cef9bde460b34542a8ef7f43538` | twsapi_doc_rendered.html | https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/ |
| 13 | 2026-10-18T08:37:35Z | get | 0 | 362740 | `af25f77fe59333e4960fef177307a56645b9683d62bed66c02effc9c48f62206` | tws_md_historical_bars.html | https://www.interactivebrokers.com/docs/tws-api/doc/md/historical-bars |
| 14 | 2026-10-18T08:37:41Z | get | 0 | 270187 | `6218f8af3959e7cff33668654b54c56b199c8148b63475d098ad544a9300634a` | tws_md_delayed-data.html | https://www.interactivebrokers.com/docs/tws-api/doc/md/delayed-data |
| 15 | 2026-10-18T08:37:46Z | get | 0 | 272756 | `cf76a969ada9b54a6be05998d7335025e238183ba3ee5608f70fba747133278a` | tws_md_earliest-data-point.html | https://www.interactivebrokers.com/docs/tws-api/doc/md/earliest-data-point |
| 16 | 2026-10-18T08:37:51Z | get | 0 | 454416 | `1b4dfbdd85acf1587b074dd13d278e8fc74dafdc7b7d91bd67a5efe083b2fe13` | tws_md_streaming-data.html | https://www.interactivebrokers.com/docs/tws-api/doc/md/streaming-data |
| 17 | 2026-10-18T08:37:57Z | get | 0 | 248788 | `a99772ee1b3c64d4e63dbadc68126bcb16bd4518596ab1ab2a10fe7dd3b1cd3c` | tws_md_introduction.html | https://www.interactivebrokers.com/docs/tws-api/doc/md/introduction |
| 18 | 2026-10-18T08:38:03Z | get | 0 | 636639 | `32c354b0109498e6a8ebe3cf0d8406558c116a6614fa5bb5c57af0761b993e7f` | tws_error-handling_error-codes.html | https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/error-codes |
| 19 | 2026-10-18T08:38:10Z | get | 0 | 234077 | `2f4e96db54397fb5b4fff64f30c97a1077968c3f57ee7400f571a7199d95328e` | tws_pacing-limitations_introduction.html | https://www.interactivebrokers.com/docs/tws-api/doc/pacing-limitations/introduction |
| 20 | 2026-10-18T08:38:16Z | get | 0 | 233897 | `5bfa73f399c36e855f5cf8c671a08f36b020c7677e8bb3097b7da3f640008652` | tws_pacing-limitations_pacing-behavior.html | https://www.interactivebrokers.com/docs/tws-api/doc/pacing-limitations/pacing-behavior |
| 21 | 2026-10-18T08:38:21Z | get | 0 | 238394 | `7524d0a257815cfcfde02fc7826513310d379db215811a287404f17dbcf039ce` | tws_tws-settings_daily-weekly-reauthentication.html | https://www.interactivebrokers.com/docs/tws-api/doc/tws-settings/daily-weekly-reauthentication |
| 22 | 2026-10-18T08:38:28Z | get | 0 | 244572 | `21b7b8ea656c9d0e050f54fda67155bf5d20972639658e13a5151785720b944d` | tws_tws-settings_historical-date-format.html | https://www.interactivebrokers.com/docs/tws-api/doc/tws-settings/historical-date-format |
| 23 | 2026-10-18T08:38:34Z | get | 0 | 236701 | `3bca1bd6438dcfe4f7d6c1dfb7fed6b9ab18ef2866ca7b4d13437a7dd1856188` | tws_notes-limitations_supported-two-factor-authentication-2-fa.html | https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/supported-two-factor-authentication-2-fa |
| 24 | 2026-10-18T08:38:40Z | get | 0 | 246199 | `5852f7891c2573f864471e42d78596092d5b488a799564bbdb50a6068547d556` | tws_notes-limitations_tws-api-limitations.html | https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/tws-api-limitations |
| 25 | 2026-10-18T08:38:46Z | get | 0 | 233547 | `25fb659c060a5b061493d51dd4dc5547a855434cb40a0305f46a062dd3d50cfe` | tws_notes-limitations_requirements.html | https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/requirements |
| 26 | 2026-10-18T08:38:53Z | get | 0 | 236514 | `de0c54a8e97a44d7320996b9b7941c32d84faa6a418f07f3656126c97422cde2` | tws_architecture_the-trader-workstation_the-ib-gateway.html | https://www.interactivebrokers.com/docs/tws-api/doc/architecture/the-trader-workstation/the-ib-gateway |
| 27 | 2026-10-18T08:39:00Z | get | 0 | 257316 | `c41a72e9e7309a1b35cfcc15ccc680ab3093fc0c7e37e215ac4105f447652a39` | tws_connectivity_establishing-an-api-connection.html | https://www.interactivebrokers.com/docs/tws-api/doc/connectivity/establishing-an-api-connection |
| 28 | 2026-10-18T08:39:06Z | get | 0 | 239004 | `fa7622ca24df632d75a91cc6a7c47ebc7491c9f54da055caeee70bedf1c3bfb1` | tws_contracts-financial-instruments_the-contract-object.html | https://www.interactivebrokers.com/docs/tws-api/doc/contracts-financial-instruments/the-contract-object |
| 29 | 2026-10-18T08:39:13Z | get | 0 | 236915 | `4229578cf827358eed1ffe576d61a103cc8dad1709f0479258d748f83e778520` | tws_trader-workstation-and-ib-gateway_download-tws-or-ib-gateway.html | https://www.interactivebrokers.com/docs/tws-api/doc/trader-workstation-and-ib-gateway/download-tws-or-ib-gateway |
| 30 | 2026-10-18T08:39:19Z | get | 0 | 239592 | `653216ee9cc54363b21edb883c2e08cc999f6ff5b1271fe4778ef8dad11ab737` | tws_error-handling_common-error-resolution_requested-market-data.html | https://www.interactivebrokers.com/docs/tws-api/doc/error-handling/common-error-resolution/requested-market-data-requires-additional-subscription-for-api-see-link-in-market-data-connections-dialog-for-more-details-delayed-market-data-is-available |
| 31 | 2026-10-18T08:41:14Z | get | 0 | 235711 | `90304b61e2065760692f1ee6fcaa532fd281a3924feb1f1985c765632bddbb7b` | tws_doc_tws-settings_tws-configuration-for-api-use_introduction.html | https://www.interactivebrokers.com/docs/tws-api/doc/tws-settings/tws-configuration-for-api-use/introduction |
| 32 | 2026-10-18T08:41:19Z | get | 0 | 235097 | `44c8cd3ad0a3ab96dfdf9895d2bb72f7d977f7d27d9aba24877d76d5f6806ab0` | tws_doc_connectivity_accepting-an-api-connection-from-tws.html | https://www.interactivebrokers.com/docs/tws-api/doc/connectivity/accepting-an-api-connection-from-tws |
| 33 | 2026-10-18T08:41:24Z | get | 0 | 137381 | `4fd7c566bd2c93b5385b68494d25c21c3f75ccd7126f5364dd401527d0dc18ae` | tws_contracts_introduction.html | https://www.interactivebrokers.com/docs/tws-api/contracts/introduction |
| 34 | 2026-10-18T08:41:29Z | get | 0 | 262041 | `57881b0a1eb3a5888365c7c122759e19276b0cc4178c34f94df8f45f4d712213` | tws_doc_contracts-financial-instruments_contract-details_receive.html | https://www.interactivebrokers.com/docs/tws-api/doc/contracts-financial-instruments/contract-details/receive-contract-details |
| 35 | 2026-10-18T08:41:34Z | get | 0 | 248652 | `8be05d2084b40297a7be3dd92a5cf5cfe60b41ab81cc26d4242f34683c8a315d` | tws_doc_contracts-financial-instruments_contract-details_request.html | https://www.interactivebrokers.com/docs/tws-api/doc/contracts-financial-instruments/contract-details/request-contract-details |
| 36 | 2026-10-18T08:41:39Z | get | 0 | 231929 | `5d48d9875e6c04f37805a0291a97ac56eb6cb64875442eefb3610629018af0c7` | tws_doc_contracts-financial-instruments_introduction.html | https://www.interactivebrokers.com/docs/tws-api/doc/contracts-financial-instruments/introduction |
| 37 | 2026-10-18T08:42:02Z | get | 0 | 4437 | `62484126fb029cb5f9ce1bc25f235dbc0114e66487f478aa99ea74bed3fd47f4` | tws_contracts_futures.md | https://www.interactivebrokers.com/docs/tws-api/contracts/futures.md |
| 38 | 2026-10-18T08:42:07Z | get | 0 | 690 | `d6bcee0e61896551d43b33bcca129c6f33e01829fd00b5f2c7ff3b18daa1aa76` | tws_contracts_find_details.md | https://www.interactivebrokers.com/docs/tws-api/contracts/contract-management/how-to-find-contract-details.md |
| 39 | 2026-10-18T08:42:22Z | get | 0 | 900 | `7025e7dee433c30160a6635b9c95b37451451839ec2ca231d8a6e4614c114d5b` | FAILED_403_ibkrcampus_llms.txt (HTTP 403) | https://ibkrcampus.com/docs/llms.txt |
| 40 | 2026-10-18T08:42:31Z | get | 0 | 13260 | `51dc18aac6f5950634c6e4ee8315036ca6e05258deeaedbb48902a91b33a70e9` | ibkr_docs_llms.txt | https://www.interactivebrokers.com/docs/llms.txt |
| 41 | 2026-10-18T08:42:43Z | get | 0 | 15291 | `b1ebbcd350eb932e40bc028930adac391e46cff62719b0e19fe9aa24f7ba96d5` | gen_llms.txt | https://www.interactivebrokers.com/docs/general/llms.txt |
| 42 | 2026-10-18T08:42:47Z | get | 0 | 534 | `dbfcc4bdcdf05d13c30f967752a6f0a948578ab5bf87f5010ff56e9e45cf13c1` | gen_mds_introduction.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/introduction.md |
| 43 | 2026-10-18T08:42:52Z | get | 0 | 1001 | `dfcafff8d2d21cd023f1cf4fbe3e96a85ebc2ec1cfa4669346d0e929ab74ff93` | gen_mds_market-data-requirements.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-requirements.md |
| 44 | 2026-10-18T08:42:58Z | get | 0 | 1736 | `06b35874470cdf0093fcf480495b4546a56c67276646732fecefe1315023010a` | gen_mds_market-data-subscription-minimum-equity-balance-requirements.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-subscription-minimum-equity-balance-requirements.md |
| 45 | 2026-10-18T08:43:03Z | get | 0 | 565 | `7c8b6670876553d8ff2fbc0dc83e6e7b39b5bb5fc54f4bc3b4c68d6034b886df` | gen_mds_support-for-market-data-subscriptions.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/support-for-market-data-subscriptions.md |
| 46 | 2026-10-18T08:43:26Z | get | 0 | 596 | `7d34719a0d9860ec2fa25f93642309644734943ea467e5983867c28ae26cce27` | gen_mds_market-data-users_market-data-sharing.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-users/market-data-sharing.md |
| 47 | 2026-10-18T08:43:31Z | get | 0 | 394 | `c9764ccccf585649d47ee8c24fde94f7139601a484088a152bcd54f5d6c3e4ec` | gen_mds_market-data-users_introduction.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-users/introduction.md |
| 48 | 2026-10-18T08:43:36Z | get | 0 | 487 | `89408acb04efcb57e0559bc086646dc74952cce7de5910f470fc35a968401ffb` | gen_mds_market-data-users_finding-your-paper-user-credentials_introduction.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-users/finding-your-paper-user-credentials/introduction.md |
| 49 | 2026-10-18T08:43:42Z | get | 0 | 1446 | `99e2c935a80096b5e8d6aa17d3f5ff70e0a89ef221d96d74ba18a066aa84e7e5` | gen_mds_tws-data-vs-api-data.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/tws-data-vs-api-data.md |
| 50 | 2026-10-18T08:43:47Z | get | 0 | 415 | `66f407d44e80687896a55bbba6aa5b86ddba6e0a3b035160020f6a57db6c69a8` | gen_mds_market-data-costs-and-fees.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/market-data-costs-and-fees.md |
| 51 | 2026-10-18T08:43:51Z | get | 0 | 961 | `903358ae29508ab0681d48c7fd14e701608ed07c23a8fe54de375f26341d30e9` | gen_mds_understanding-market-data-subscriptions.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/understanding-market-data-subscriptions.md |
| 52 | 2026-10-18T08:43:56Z | get | 0 | 2295 | `87363eb0111f5266dca247ad1f1848006d6a4b414f9be2f28a3b2fa4ec494472` | gen_mds_popular-market-data-subscriptions_introduction.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/popular-market-data-subscriptions/introduction.md |
| 53 | 2026-10-18T08:44:02Z | get | 0 | 1118 | `d76ec27b8dd20a7db4c905d50f3847baabc90237c11f6b8ba0f12debc51c1783` | gen_mds_professional-vs-non-professional.md | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/professional-vs-non-professional.md |
| 54 | 2026-10-18T08:44:06Z | get | 1 | 0 | `NA` | gen_mds_compliance-requirements-for-api-market-data_market-data-api-acknowledg | https://www.interactivebrokers.com/docs/general/market-data-subscriptions/compliance-requirements-for-api-market-data/market-data-api-acknowledgement.md |
| 55 | 2026-10-18T08:44:26Z | get | 0 | 382116 | `de53e5f6abf89897d44c8a3a5d1820b7c01bbab57b226afaf9fae055adeb4949` | ibkr_market_data_pricing.html | https://www.interactivebrokers.com/en/pricing/market-data-pricing.php |
| 56 | 2026-10-18T08:45:42Z | get | 0 | 5727 | `c80c341784240491700afc8a4016a2050eaf73ea418a9fbe75fb1cb36c6e3c29` | ibkrguides_kb1719.html (JS shell) | https://www.ibkrguides.com/kb/article-1719.htm |
| 57 | 2026-10-18T08:45:54Z | fetch | 0 | 40133 | `7383f13caf07314424a0d156af78c15c2047172e897c8caa3d8ea582819597b6` | ibkrguides_kb1719_rendered.html (rendered before content loaded) | https://www.ibkrguides.com/kb/article-1719.htm |
| 58 | 2026-10-18T08:46:10Z | fetch+idle+wait4000 | 0 | 54223 | `98f8f6ed95af3b4e241873b93ef823391d0568b5158e79b07969b40a77031098` | ibkrguides_kb1719_rendered2.html | https://www.ibkrguides.com/kb/article-1719.htm |
| 59 | 2026-10-18T08:46:34Z | get | 0 | 406 | `8b0c8bb11ce5ea1decad1804dc2b8ec862dfb2a096f70a31388700442d146044` | FAILED_404_tws_paper_trading_limitations.md (page not found) | https://www.interactivebrokers.com/docs/tws-api/doc/notes-limitations/limitations/paper-trading.md |
| 60 | 2026-10-18T08:46:57Z | fetch+idle+wait3000 | 0 | 63136 | `9aca45c776b4381ce3bf2d40f60c6657e98e05412b9d79ae27842620cb4ba6b2` | ibkrguides_cp_aboutpaper.html | https://www.ibkrguides.com/clientportal/aboutpapertradingaccounts.htm |
| 61 | 2026-10-18T08:47:08Z | fetch+idle+wait3000 | 0 | 61140 | `6ca227775eddec110fb54d50f2860d39712fe91fbfbc9b4bc94e543a2d60ee09` | ibkrguides_cp_paperaccount.html | https://www.ibkrguides.com/clientportal/papertradingaccount.htm |
| 62 | 2026-10-18T08:47:26Z | get | 0 | 660317 | `ef2886c5b0e07b32a551715dc601a0bc676b58dfb46ce2065c4f5742372dd6da` | campus_request-paper-trading-account.html | https://www.interactivebrokers.com/campus/trading-lessons/request-paper-trading-account/ |
| 63 | 2026-10-18T08:47:31Z | get | 0 | 630757 | `aeda984e89bfb4a5c306f4d8967fde2f85d9aa5b0c704c2616d1b00770f5892c` | campus_how-to-open-an-ibkr-paper-trading-account.html | https://www.interactivebrokers.com/campus/trading-lessons/how-to-open-an-ibkr-paper-trading-account/ |
| 64 | 2026-10-18T08:47:36Z | get | 0 | 603554 | `4ffaf474893e673814ca1c969f33ead6c9bf3744bf566eae8ed941a483bf5c6a` | campus_how-to-sign-up-for-an-interactive-brokers-paper-trading-account.html | https://www.interactivebrokers.com/campus/ibkr-quant-news/how-to-sign-up-for-an-interactive-brokers-paper-trading-account/ |
| 65 | 2026-10-18T08:48:00Z | get | 0 | 12983 | `3854fb4671eaa6a7f2c94496f56a45b0f0226325c2304cc0652639ba378f0752` | tpi_general_faq.md | https://www.interactivebrokers.com/docs/third-party-integrations/general-third-party-frequently-asked-questions.md |
| 66 | 2026-10-18T08:48:08Z | get | 0 | 12200 | `e6036c1e25df3bca087138b5881a234d0cd7ae03db781db668b0a924efcf5b2c` | legacy_historical_limitations.html | https://interactivebrokers.github.io/tws-api/historical_limitations.html |
| 67 | 2026-10-18T08:48:11Z | get | 0 | 48334 | `fb3362c4bbc7b5f0f3f900d8b8354c9179391cef51137a21c6fb80646967a197` | legacy_historical_bars.html | https://interactivebrokers.github.io/tws-api/historical_bars.html |
| 68 | 2026-10-18T08:48:13Z | get | 0 | 15923 | `8ba7d24d43cb7d09c8dda7ff4839b93c4f7ee840cfbab2b2a27352e2d04c6ec0` | legacy_market_data_type.html | https://interactivebrokers.github.io/tws-api/market_data_type.html |
| 69 | 2026-10-18T08:48:16Z | get | 0 | 9702 | `ef0ccc0f9de8312c7247fa4e68675e6d6ed8d534b19c4f93d3efe9054bc12f2b` | legacy_delayed_data.html | https://interactivebrokers.github.io/tws-api/delayed_data.html |
| 70 | 2026-10-18T08:48:19Z | get | 0 | 61366 | `a029070330e6c6ab2ea4fafa1973a83c04444828055d1c86ffa306aaa9376f75` | legacy_message_codes.html | https://interactivebrokers.github.io/tws-api/message_codes.html |
| 71 | 2026-10-18T08:48:21Z | get | 0 | 40381 | `8fcbd3a805376ae24cd55d0e51f2809f114b9c1190dd2e00875d0ef91fb1d5cc` | legacy_tick_types.html | https://interactivebrokers.github.io/tws-api/tick_types.html |
| 72 | 2026-10-18T08:48:24Z | get | 0 | 86344 | `ebdbc3db5a09c35022a9960eb820e5a57a98ad06f8f4661bb8018240fe6318ac` | legacy_basic_contracts.html | https://interactivebrokers.github.io/tws-api/basic_contracts.html |
| 73 | 2026-10-18T08:48:26Z | get | 0 | 10747 | `b6715287bc92258e384e38022400c55ce41320cee4a5473f6e56d9d75c610198` | legacy_historical_data.html | https://interactivebrokers.github.io/tws-api/historical_data.html |
| 74 | 2026-10-18T08:48:29Z | get | 0 | 9308 | `179c0cd4b965ba8e174dd373bc302c71cd6003d74f07530d298eb6f3e5c42164` | FAILED_404_legacy_paper_trading.html (GitHub Pages 404) | https://interactivebrokers.github.io/tws-api/paper_trading.html |
| 75 | 2026-10-18T08:48:31Z | get | 0 | 16911 | `69bb99c34b7560e03ec0c560e2d016ac0e12a5649dc37fb9af5237909c6b08cb` | legacy_initial_setup.html | https://interactivebrokers.github.io/tws-api/initial_setup.html |
| 76 | 2026-10-18T08:49:16Z | get | 0 | 3850 | `21e049d5f9ddb7611229ac694c31b32b121e7a2aefa27468868fcb74574aaabc` | tws_syncdoc_historical_market_data.md | https://www.interactivebrokers.com/docs/tws-api/sync-doc/historical-market-data.md |
| 77 | 2026-10-18T08:49:31Z | get | 0 | 19844 | `44b7876208428e79973b5553c29c1130224ddde2d9d9ab66c3ddcf14dbb01282` | tws_md_historical_bars.md | https://www.interactivebrokers.com/docs/tws-api/doc/md/historical-bars.md |
| 78 | 2026-10-18T08:50:03Z | fetch+idle+wait3000 | 0 | 63888 | `34d0a9e8bfd43c865815d13fcac3b5fa900bef2edc00bb926f9534b1fcf34cb1` | ibkrguides_tws_futures_term_structure.html | https://www.ibkrguides.com/traderworkstation/futures-term-structure.htm |
| 79 | 2026-10-18T08:50:13Z | fetch+idle+wait3000 | 0 | 87959 | `d1f25ab320ab474b5baf8388c22f862d09c23b35ec9af76e1affd0452430391e` | ibkrguides_tws_prices.html | https://www.ibkrguides.com/traderworkstation/prices.htm |
| 80 | 2026-10-18T08:50:20Z | get | 0 | 604961 | `810d610aba6c3834d904ee10f556e125790462a90b75561169603ed9c419aa57` | campus_close-price.html | https://www.interactivebrokers.com/campus/trading-lessons/close-price/ |
| 81 | 2026-10-18T08:50:31Z | get | 0 | 987 | `e6c7aad46a0eacf9448d7f6d742f4ff892ea52a87051867343bef2cf3bf0c25a` | ninjatrader_forum_robots.txt | https://forum.ninjatrader.com/robots.txt |
| 82 | 2026-10-18T08:50:36Z | get | 0 | 27338 | `f17b6ff600edeeef5af52221943cd95401cc2629d75e7d32aaba08b8da9f838a` | FAILED_jsshell_thirdparty_ninjatrader_98367.html (JS shell, no thread text; not used) | https://forum.ninjatrader.com/forum/ninjatrader-7/platform-technical-support/98367-nt7-daily-bar-settlement-price-problem-with-interactive-brokers-data-feed |
| 83 | 2026-10-18T08:50:45Z | get | 0 | 46326 | `93cd95c1ddfd18e204e93aef659defd8567fc1a332a9e4c4a0da2c4b5d8f9afd` | ibc_userguide.md | https://raw.githubusercontent.com/IbcAlpha/IBC/master/userguide.md |
| 84 | 2026-10-18T08:50:49Z | get | 1 | 0 | `NA` | ibc_config.ini | https://raw.githubusercontent.com/IbcAlpha/IBC/master/resources/config.ini |
| 85 | 2026-10-18T08:50:51Z | get | 1 | 0 | `NA` | ibc_gatewaystart.sh | https://raw.githubusercontent.com/IbcAlpha/IBC/master/resources/gatewaystart.sh |
| 86 | 2026-10-18T08:50:54Z | get | 0 | 7167 | `dc367dd513ac66c5ea86589cee29f8f8ab19560a6371a09c708a423a3c3396b7` | ibc_README.md | https://raw.githubusercontent.com/IbcAlpha/IBC/master/README.md |
| 87 | 2026-10-18T08:51:02Z | get | 0 | 35145 | `4ae36d1b0b65cd106d303ff7f9e59784da270c4864aeb274f03648678d337955` | ibc_config_ini.txt | https://raw.githubusercontent.com/IbcAlpha/IBC/master/resources/config.ini |
| 88 | 2026-10-18T08:51:04Z | get | 0 | 7696 | `0b6f4ce7a22d597d6ec48c266f872139da8f9a614ab80056f5000668848e6d65` | ibc_gatewaystart_sh.txt | https://raw.githubusercontent.com/IbcAlpha/IBC/master/resources/gatewaystart.sh |
| 89 | 2026-10-18T08:51:41Z | fetch+idle+wait3000 | 0 | 54272 | `2ad8aa44d88bdcdba59a21cbea9d806941f397b5b5b85b2383c959a1f4cba814` | ibkrguides_tws_auto_restart_considerations.html | https://www.ibkrguides.com/traderworkstation/auto-restart-considerations.htm |
| 90 | 2026-10-18T08:52:02Z | get | 0 | 628924 | `74f6102c1b50c690d8a4124d1347ddbee1360f33e673628b9259667d9a8e679b` | campus_installing-configuring-tws-for-the-api.html | https://www.interactivebrokers.com/campus/trading-lessons/installing-configuring-tws-for-the-api/ |
| 91 | 2026-10-18T08:52:07Z | get | 0 | 674858 | `df3ea0af59b428796df80a9849418d3e8b15fd37d3815a030f562834521b912c` | campus_launching-and-authenticating-the-gateway.html | https://www.interactivebrokers.com/campus/trading-lessons/launching-and-authenticating-the-gateway/ |
| 92 | 2026-10-18T08:52:18Z | get | 0 | 194791 | `b8f7af6adbb3e9464fa08df4c6e2aaee809b9b3ee92e1a259be6e27e61fb4fc2` | ibkr_ibgateway_stable.html | https://www.interactivebrokers.com/en/trading/ibgateway-stable.php |
| 93 | 2026-10-18T08:52:45Z | get | 0 | 186739 | `03cf294fe1322b9b38766aad9286effe8d8573b5f305a91638f2e7536da4d36e` | github_ibc_releases_latest.html | https://github.com/IbcAlpha/IBC/releases/latest |
| 94 | 2026-10-18T08:53:04Z | get | 0 | 1922962 | `64198f28480ef76be97f0a969bfee886c5dd8d71f6c81a6c59b9185369ae0c66` | ibasync_api.html | https://ib-api-reloaded.github.io/ib_async/api.html |
| 95 | 2026-10-18T08:53:08Z | get | 0 | 112383 | `eb44597a53893f9154c24346fead7c2d20d369a8945a5af417def8999bc27bda` | ibasync_changelog.html | https://ib-api-reloaded.github.io/ib_async/changelog.html |
| 96 | 2026-10-18T08:53:12Z | get | 1 | 0 | `NA` | ibasync_pypi.json | https://pypi.org/pypi/ib-async/json |
| 97 | 2026-10-18T08:53:12Z | get | 0 | 15374 | `d67ef106b339792eea5260e41da66a77861e398ff8c06c30a43ace7865743c7a` | ibasync_README.md | https://raw.githubusercontent.com/ib-api-reloaded/ib_async/main/README.md |
| 98 | 2026-10-18T08:53:18Z | get | 0 | 2825 | `72f3a0713024ae63bfbb8d09e2530b1c9f5d0927294830a9b2aadb845e8c036b` | FAILED_challenge_ibasync_pypi.html (PyPI client challenge; not used) | https://pypi.org/project/ib-async/ |
| 99 | 2026-10-18T08:53:55Z | get | 0 | 47071 | `a4122634a124a80c1139e2097868422983a0596f4d9257af90932b4422c6ab8b` | ibasync_wrapper_py.txt | https://raw.githubusercontent.com/ib-api-reloaded/ib_async/main/ib_async/wrapper.py |
| 100 | 2026-10-18T08:54:02Z | get | 0 | 14999 | `c06ec217476a892c2387e56f62fc155b4b226fcecd6ebd713af62d533085e4fa` | ibasync_util_py.txt | https://raw.githubusercontent.com/ib-api-reloaded/ib_async/main/ib_async/util.py |
| 101 | 2026-10-18T08:54:10Z | get | 0 | 190870 | `3ebb77f678e559ae7bfd7ef8c9af6e2d15bac45e8754c727f727aa229efda8a5` | FAILED_redirect_ibkr_products_cbot_fut.html (redirected to JS product search; not used) | https://www.interactivebrokers.com/en/index.php?f=2222&exch=cbot&showcategories=FUTGRP&limit=100&page=1 |
| 102 | 2026-10-18T08:54:28Z | get | 0 | 314118 | `0325a836fdfe3cb8a58da826f0995881c35d16a92dc1f2136b8e192c38be3df6` | ibkr_margin_futures_fops.html (redirected to general margin page; superseded by ibkr_margin_futures_fops_us.html) | https://www.interactivebrokers.com/en/trading/margin-futures-fops.php |
| 103 | 2026-10-18T08:54:49Z | get | 0 | 197360 | `50bd60b06473f575715ac8e182824b95d799b433227b3055d007b7322cddae8c` | ibkr_micro_futures_comparison.html | https://www.interactivebrokers.com/en/trading/micro-futures-comparison.php |
| 104 | 2026-10-18T08:54:53Z | get | 0 | 648699 | `075278af67f6b250a0951c731dbafec673a4e0a5df21ea77001052130e7b6f02` | ibkr_margin_futures_fops_us.html | https://investors.interactivebrokers.com/en/trading/margin-futures-fops.php?hm=us&ex=us&rgt=0&rsk=1&pm=0&rst=101004100808080101 |
| 105 | 2026-10-18T08:55:29Z | get | 0 | 8506 | `049d4c68a33f83d907db69c63384414a540cb2d79b2392d0464f92d3ea886657` | tws_changelog.md | https://www.interactivebrokers.com/docs/tws-api/changelog.md |
