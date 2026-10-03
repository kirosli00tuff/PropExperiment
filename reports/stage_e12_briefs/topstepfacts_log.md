# TopstepFacts fetch log (Stage E.12 Task 2b)

Worker: TopstepFacts-OpusMedium. Date 2026-10-03. All fetches by `curl -sL` with a desktop
Chrome User-Agent (no login, no cookies). No WebSearch, WebFetch, Scrapling, Firecrawl or Wayback
was needed: every help.topstep.com page answered 200 to curl. robots.txt of help.topstep.com pages:
`<meta name="robots" content="all">`; www.topstep.com/robots.txt disallows only /api and
/design-pages. No TopstepX or ProjectX page or API touched.

Pages folder: reports/stage_e12_briefs/topstep_pages/

| # | URL (final) | HTTP | Fetched UTC | Fetched PDT | Page dateModified (JSON-LD) | Saved file | sha256 |
|---|---|---|---|---|---|---|---|
| 1 | https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan | 200 | 2026-10-03T15:27:06Z | 08:27:06 | 2026-07-16T14:03:03Z | art_8284223.html | ba3cd3b0abdc413af3c3aafad38392a4a09b1bca42ac8f2a4109a5dd408e21b2 |
| 2 | Image "XFA charts - hc.png" embedded in #1 (downloads.intercomcdn.com/i/o/bjnr216i/2431115610/e9b4f24c46bea0fcd5c4e3d008d7/19155321446035?expires=1791043200&signature=...) | 200 image/png | 2026-10-03T15:27:11Z | 08:27:11 | (same as #1) | scaling_xfa_charts.png (5515x2474) | 55ec76b4b293822849c9bf8a8ac2de362fa895010d39ce9c0d00f4ed275e6cbd |
| 3 | https://help.topstep.com/en/articles/8284215-express-funded-account-parameters | 200 | 2026-10-03T15:27:40Z | 08:27:40 | 2026-08-05T19:49:02Z | art_8284215.html | 16af87ffa2bc5fecee76410a63867a7ec52d95d2102012a2cba1d67f9ca769b5 |
| 4 | https://help.topstep.com/en/articles/8284197-trading-combine-parameters | 200 | 2026-10-03T15:27:41Z | 08:27:41 | 2026-09-24T20:21:06Z | art_8284197.html | 9181f4511ab87625ba32245c8a8f4d20b5c277e17d2ea9bab25c06767fec46a0 |
| 5 | https://help.topstep.com/en/articles/8284128-what-is-a-reset | 200 | 2026-10-03T15:27:41Z | 08:27:41 | 2026-09-25T22:00:43Z | art_8284128.html | 31d80d9f91219bb6231aaa0808f12459d3065b558ebcb7085cd802b8799b1e18 |
| 6 | https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions | 200 | 2026-10-03T15:27:42Z | 08:27:42 | 2026-09-04T12:58:40Z | art_8284121.html | 0cd197bae16607a621f60b7ee19b771788bdbd8ab257ffa47ff79ed890b695d3 |
| 7 | https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions | 200 | 2026-10-03T15:27:42Z | 08:27:42 | 2026-09-25T22:00:42Z | art_14289835.html | 36eb6af9d8d426c8adaa5db68079ae6341e98c1865a43d03b6fae7628824bec4 |
| 8 | https://help.topstep.com/en/articles/12060405-back2funded-rules-guidelines-and-how-it-works | 200 | 2026-10-03T15:27:43Z | 08:27:43 | 2026-09-29T20:43:51Z | art_12060405.html | a3e4d0af73cceb87d9ee22448e78c5ebec9adefc6cd2de1cc80fb313589931ea |
| 9 | https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit | 200 | 2026-10-03T15:27:56Z | 08:27:56 | 2026-09-18T18:51:37Z | art_8284204.html | e42229a995b804d5b2f27239bb11a33978d64a31d7e5fd8ea886391ae8016f84 |
| 10 | https://help.topstep.com/en/articles/8284217-express-funded-account-activation | 200 | 2026-10-03T15:27:57Z | 08:27:57 | 2026-09-24T20:17:59Z | art_8284217.html | fd429c1a3c7203fbbbceb74790f0a7c2d62319299a83ef2f75d4fe35509018ba |
| 11 | https://www.topstep.com/pricing | 404 | 2026-10-03T15:28:02Z | 08:28:02 | n/a | not kept (404 page) | n/a |
| 12 | https://www.topstep.com/ | 200 | 2026-10-03T15:28:02Z | 08:28:02 | none in page | topstep_com_home.html | 3a172a8d4a53b5006090038b8e069a9d712a42a422a6c6f6d99b33a52ee6bb04 |

Other requests (not evidence, not kept):
- help.topstep.com/en/?q=<term> for "maximum loss limit", "back2funded", "reset", "minimum trading
  days", "pricing", "activation fee" at about 15:27:20Z: used only to find article links; the
  static HTML carried links for "reset" only. Article links were then taken from the "Related
  Articles" and in-body links of #1, #4, #3.
- www.topstep.com/robots.txt and www.topstep.com/sitemap.xml at about 15:28Z: the sitemap lists no
  pricing page (grep for pric/combine/plan returned only blog posts). The static homepage (#12)
  contains no 150K price text (prices appear to be rendered by script); the help-center pricing
  article (#7) is used as the pricing source.

Reading method: each HTML was converted to text by a throwaway script (tags stripped, entities
unescaped) and grepped; the derived .txt files were deleted afterwards and can be regenerated from
the raw HTML. The scaling image was downscaled to 1600 px wide in the session scratchpad and read
with the Read tool; the raw full-size PNG is the saved evidence.

No search-budget notice was seen (no WebSearch call was made). No block or terms barrier was met.
