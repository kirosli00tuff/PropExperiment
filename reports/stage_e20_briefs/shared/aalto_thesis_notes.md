# Aalto thesis notes (Stage E.20 Part A, shared source; reader ProductReader-ZN-OpusHigh)

Written 2026-10-11 (PDT). Other readers cite this file as
`reports/stage_e20_briefs/shared/aalto_thesis_notes.md`.

## Bottom line for other readers

**The full text could not be retrieved, so no per-asset-class or per-market number is available.**
The repository gives the record as metadata only: no file is attached, and the full text can be read only
on Aalto's restricted Thesis Database, which blocks saving a copy. Everything below comes from the
repository's own metadata record, read through its public REST API. The abstract is primary text (the
author's own abstract, served by the repository). It gives **no figures**: no gross, no net, no
per-market rows. Any claim that cites this thesis for a number is [unverified].

Corrections to the planning brief (`literature_planning_2026-10-10.md`, finding 1 and source list):
- The thesis covers **equity, bond and currency futures only (20 futures)**, not "every asset class".
  It has **no commodities**: no energy, metals, grains or livestock. CL, NG, GC, ZC, ZS, ZL, HE and LE
  readers should not cite it for class evidence.
- Sample: "January 2008 to October 2024". Issued 2025 (accessioned 2025-03-02).
- "mostly not after costs, especially bonds and FX" matches the abstract. The abstract says
  "may not be feasible" and gives no cost model or numbers.

## Identification

| Field | Value (verbatim from the metadata) |
|---|---|
| Title | "Intraday momentum in futures markets" (Finnish: "Päivänsisäinen momentum futuurimarkkinoilla") |
| Author | "Majorin, Justus" |
| Advisor | "Suominen, Matti" |
| School / department | "School of Business" / "Rahoituksen laitos" (Department of Finance) |
| Programme | "Finance" |
| Type | "Master's thesis" ("G2 Pro gradu, diplomityö") |
| Issued | "2025" |
| Extent | "81+21" (pages) |
| Handle / URN | https://aaltodoc.aalto.fi/handle/123456789/134393 ; "URN:NBN:fi:aalto-202503022652" |
| Open access | `local.aalto.openaccess`: "no"; `local.aalto.electroniconly`: "yes"; `dc.location`: "P1 I" |
| Access status (API) | `"status" : "metadata.only"`, `"embargoDate" : null` |
| Bundles (files) | none (`"totalElements" : 0`) |

## Abstract (verbatim, English, from `dc.description.abstract`)

> In this thesis, we study intraday momentum and return reversal patterns in equity, bond and currency
> futures markets. Earlier research has demonstrated the existence of intraday momentum by showing that
> the returns of earlier periods within the same trading day positively predict the last half an hour
> returns of the same day. The intraday momentum phenomenon has been documented globally across various
> asset classes. We build on the prior research by employing a futures dataset comprising 20 futures
> indices in equities, bonds and currencies. We first show that the intraday momentum patterns still
> exist in our dataset spanning January 2008 to October 2024.
>
> In our empirical analysis, we then extend the literature by showing that most of the predictability in
> the return of the last half an hour stems from the last ten-minute period, which we link to hedging and
> rebalancing needs of option writers and leveraged ETFs, who seek to trade as near to the close as
> possible. Furthermore, we study the reversal of the last half an hour return in greater detail than
> prior research, and show that the last half an hour return is a negative and statistically significant
> predictor of subsequent overnight and intraday returns. Additionally, we find that most intraday
> momentum and reversal trading strategies may not be feasible after transactions costs, especially in
> bond and currency futures.

Location: `reports/stage_e20_briefs/shared/aalto_thesis_item_api.json`, key
`metadata["dc.description.abstract"][0]`.

## Per asset class (what the abstract supports, and nothing more)

| Class | Momentum persists 2008-2024? | Feasible after costs? | Figures | Grade |
|---|---|---|---|---|
| Equity index futures | yes, pooled statement ("patterns still exist in our dataset") | "most ... may not be feasible"; equities not singled out as worst | none | primary (abstract), no numbers |
| Bond futures | pooled statement only | "especially" not feasible ("especially in bond and currency futures") | none | primary (abstract), no numbers |
| Currency futures | pooled statement only | "especially" not feasible | none | primary (abstract), no numbers |
| Commodities (energy, metals, grains, livestock) | not in the sample | n/a | n/a | n/a |

Per market (which of the 20 futures, which bond tenors, whether ZN, ZB, ZF or ZT are among them): **not
known.** The abstract does not list the contracts. Whether the 20 "futures indices" include US Treasury
futures, and which ones, cannot be stated. [unverified]

## Other findings stated in the abstract (no figures)

1. Most of the last-half-hour predictability comes from the **last ten minutes** before the close. The
   author links this to option-writer hedging and leveraged-ETF rebalancing. Note for E.20: the program's
   flatten F_X = 15:08 CT is after the equity close (15:00 CT) but before the rates and FX settlement
   closes. Whether the thesis's "close" is settlement or session end for bonds is not known.
2. The last-half-hour return **negatively predicts** the following overnight and intraday returns
   (statistically significant). Overnight holds are out of E.20's scope. The intraday-next-day reversal
   is a direction only, with no size given.

## Fetch log

| URL | UTC | sha256 | Saved path | Status |
|---|---|---|---|---|
| https://aaltodoc.aalto.fi/robots.txt | 2026-10-11T17:34:03Z | (502 body, not kept) | none | blocked: HTTP 502 proxy error, twice; third try timed out (17:37Z) |
| https://aaltodoc.aalto.fi/items/1011f043-edd1-4cb2-9694-b1216d77561f (curl) | 2026-10-11T17:35Z | n/a | none | blocked: HTTP 502, twice |
| same (WebFetch) | 2026-10-11T17:36Z | n/a | none | blocked: HTTP 403 |
| https://aaltodoc.aalto.fi/server/api/core/items/1011f043-edd1-4cb2-9694-b1216d77561f | 2026-10-11T17:36Z | 0d301069918a97651b2a53431dce0b924450b65f42bdf550a94158cdcae9ac46 | shared/aalto_thesis_item_api.json | ok (metadata) |
| .../items/1011f043-.../bundles | 2026-10-11T17:37Z | see JSON log in product_ZN.json | shared/aalto_thesis_bundles_api.json | ok (empty: no files) |
| .../items/1011f043-.../accessStatus | 2026-10-11T17:37Z | see product_ZN.json | shared/aalto_thesis_accessstatus_api.json | ok ("metadata.only") |
| https://aaltodoc.aalto.fi/info/end-user-agreement | 2026-10-11T17:38Z | n/a | none | blocked: timed out |
| https://www.aalto.fi/en/news/aalto-thesis-database-now-available-from-outside-the-learning-centre | 2026-10-11T17:39:39Z | see product_ZN.json | shared/aalto_thesis_database_news.html (+ .txt) | ok |

Access rule, verbatim from the Aalto news page (published 8.1.2024): "Aalto Thesis Database is a remote
desktop connection to Aaltodoc, an archive of full-text versions of master's, licentiate, and doctoral
theses that are otherwise subject to access restrictions, due to lack of authorial permission." And: "You
can read the thesis on screen or get it printed on paper. However, a block prevents saving a copy onto
your own device." The database is open to "all visitors at a Harald Herlin Learning Centre's public
Windows workstations" and to Aalto students and staff. **No automated route to the full text exists, and
none was attempted.**

Terms: aaltodoc's robots.txt and end-user agreement could not be read (502 and timeouts). The three API
calls were single GETs of public metadata, the same data the public item page shows. No full text was
requested or exists for download. Recorded as a gap: terms unread because the site was unreachable.

## For the lead

- The only route to the per-class numbers is a person at the Aalto Learning Centre workstation, or the
  author (contact not searched; outside a reader's brief).
- Until then, cite the thesis only for the direction of its statements: persistence through 2024, the
  last-10-minute concentration, the reversal, and infeasibility after costs, "especially" for bonds and FX.
