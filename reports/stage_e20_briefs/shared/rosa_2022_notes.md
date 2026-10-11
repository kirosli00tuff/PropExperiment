# Rosa (Journal of Futures Markets 2022): shared notes (threshold form)

Reader: ProductReader-NQ-OpusHigh (Stage E.20 Part A), written 2026-10-11 (PDT). Cite as
`reports/stage_e20_briefs/shared/rosa_2022_notes.md`.

## Bottom line

**The full text could not be retrieved under the program's web rules, so the threshold's definition,
value, lookback, the sample and every figure are [unverified].** Only the abstract is primary text. The
abstract states that a threshold strategy beats an always-on one and that predictability disappears out
of sample; it gives no number.

## Record

- Carlo Rosa, "Understanding intraday momentum strategies", Journal of Futures Markets 42(12), 2218-2234,
  first published 2022-09-08, doi 10.1002/fut.22375. Affiliation per OpenAlex: University of Calabria.
- RePEc/IDEAS record saved: `shared/rosa_ideas.html`
  (https://ideas.repec.org/a/wly/jfutmk/v42y2022i12p2218-2234.html, fetched 2026-10-11T17:36:09Z, sha256
  d4bf996acfc622a6e267d8705c018a083919814caf77ac37b17b8ffbb54f36b9). Its "File URL" is the DOI; "Download
  Restriction: no" there refers to the RePEc listing, not to open access.
- OpenAlex record saved: `pages/NQ/rosa_openalex.json` (sha256
  8a709d6fddc57d0e518eef5838ddca4f07d12176aa834b249a8a17d9cf97517b): `'is_oa': False, 'oa_status':
  'closed', 'oa_url': None, 'any_repository_has_fulltext': False`; one location, the publisher.

## Abstract (verbatim, from the saved IDEAS record, `abstract-body`)

> This paper studies the out‐of‐sample performance of the intraday momentum strategy where the overnight
> return predicts the return of the last half‐hour of trading. The predictability disappears in the
> out‐of‐sample period. A Markov‐switching model endogenously identifies two distinct regimes and suggests
> that the predictability depends on the strength of the signal. Hence, assessing return predictability in
> calendar time may lead to false conclusions when anomalies feature time‐varying returns. The paper
> documents that understanding the return dynamics is important for an effective strategy implementation.
> A strategy with thresholds delivers higher returns than a strategy that is always active.

What the abstract establishes (primary): the predictor is **the overnight return**, not Baltussen's
r_ROD; the target is the last half-hour return; out-of-sample predictability disappears; a threshold
strategy earns more than an always-active one. Nothing else.

## Secondary statements (not verified against the paper)

- Zarattini, Aziz, Barbon (2024 working paper, saved by E.13 as
  `reports/stage_e13_briefs/pages/InfoSource/unisg_intraday_mom.pdf.txt`, sha256
  186a6cf173c77067905aa8c8244a8f582c47f34a58d5749e243863baae2e573e), lines 72-77: "Rosa [7] analyzes
  additional data post2013, noting a decline in predictability, which he attributes to market adaptations
  or the ephemeral nature of previously exploitable inefficiencies. His application of a Markovswitching
  model underlines how the intraday momentum's effectiveness is contingent upon volatile market regimes."
  [secondary-only]
- Search-result snippets (WebSearch, 2026-10-11, not retrieved text; sources named by the search tool as
  the Wiley abstract page, ResearchGate and vLex): "the strategy is triggered and becomes active only when
  the absolute value of the overnight return is larger than a given threshold"; data "intraday futures
  data on S&P 500, Nasdaq 100, and DJIA were obtained from Pi trading"; a figure caption with a sample of
  "September 1997–December 2020". **[unverified: search snippet only]**. The threshold's value, how it is
  set (fixed, rolling percentile, in-sample optimum), its lookback and the per-index results are not
  known.

## Access attempts (all logged in `pages/NQ/fetch_log.txt`)

| Source | Result |
|---|---|
| onlinelibrary.wiley.com/doi/full/10.1002/fut.22375 (curl) | 403, Cloudflare challenge. |
| Wiley terms, https://onlinelibrary.wiley.com/terms-and-conditions (read via scrapling fetch after curl 403 and scrapling get challenge; saved `pages/NQ/wiley_terms_scrapling_fetch.md`, sha256 2a5622a9136aac4b608e9a7f6d201d88ca10e92015bea19dced93cabd54f7a82) | Forbids automated access: "Use any scraper, crawler, spider, robot or other automated means of any kind to access or copy this site, Wiley Online Library, the Electronic Products, or any material included therein" (line 86). Not fetched further: terms-forbid. |
| vLex (law-journals-books.vlex.com) | Terms (https://vlex.com/terms, saved `pages/NQ/vlex_terms.html`, sha256 d5d90f41a2208df9a79a99d711d511916db3b0a349531dd0ce3e5ba4a5f94404): "(e) Prohibition on Automated Access. Accessing or using the Services through automated means, including robots, spiders, generative AI solutions not provided by us, or data mining tools, is strictly forbidden". Not fetched: terms-forbid. |
| ResearchGate | Not attempted (its terms forbid automated access; E.13 practice). |
| colab.ws/articles/10.1002/fut.22375 (WebFetch) | Abstract only; no sample, threshold or data source. |
| OpenAlex, Unpaywall status | Closed access; no repository copy. |

A licensed copy (library or the author) is the only route to the threshold details.

## Use in E.20

- H6's T2 (|r_ROD| above the median of the previous 60 eligible dates) is **not Rosa's rule as
  published**: Rosa thresholds the overnight return (per the abstract's predictor and the unverified
  snippet), and the form of his threshold is unknown. T2 is the planning brief's own variant ("trade only
  when |r_ROD| is above its trailing median", literature_planning finding/shortlist 1), motivated by Rosa's
  qualitative result. See `product_NQ.md` section 4.
