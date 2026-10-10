# Stage E.18 listing-date evidence (lead, inline narrow lookup; 2 WebSearch calls, 2 pages kept)

Times UTC (fetch). Pages saved raw here and read by grep (html tags stripped, whitespace collapsed).

| File | URL | Fetched (UTC) | Method | Bytes | sha256 |
|---|---|---|---|---|---|
| mbt_launch_20210503.html | https://www.cmegroup.com/media-room/press-releases/2021/5/03/cme_group_announceslaunchofmicrobitcoinfutures.html | 2026-10-10T18:48:36Z | scrapling extract get (curl on investor.cmegroup.com gave 403 at 18:48:31Z) | 126305 | d96864549964b5962d61658f8fca76e76538b15a9d2a9baaab95fd0a867da239 |
| btc_selfcert_20171201.html | https://www.cmegroup.com/media-room/press-releases/2017/12/01/cme_group_self-certifiesbitcoinfuturestolaunchdec18.html | 2026-10-10T18:48:37Z | scrapling extract get (curl on investor.cmegroup.com gave 403 at 18:48:31Z) | 122580 | 64d1652f5de93d214e8ec61b9f34833352ab334084c3d40ed1f7b50194ae5e79 |

Verbatim passages:
- MBT: "CHICAGO , May 3, 2021 /PRNewswire/ -- CME Group , the world's leading and most diverse derivatives
  marketplace, today launched Micro Bitcoin futures, further expanding its suite of crypto derivatives offerings."
  (the space before each comma is the page's own markup boundary)
- BTC: "It will be available for trading on the CME Globex electronic trading platform, and for submission for
  clearing via CME ClearPort, effective on Sunday, December 17, 2017 for a trade date of December 18."

Not fetched (marked [unverified] wherever used): the exchange launch dates of NQ, ZN, 6E, GC, ZC, CL and NG. Each was
a listed CME Group product before 2010-06-07 and through 2019-04-30; C1's annex ruling C5 records "all six were mature
contracts in 2010" (reports/stage_e13_ng_replication_draft.md:439).
