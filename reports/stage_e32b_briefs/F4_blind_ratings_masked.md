# F4 blind ratings (masked), BlindScorer2-OpusXHigh

Generated 2026-10-29 03:54 PDT from the three files the brief allows (brief_blind.md, F4_masked_contracts.json, F4_masked_firms.json). Full reasons with masked item ids are in F4_blind_ratings_masked.json; this file has short reasons only. Marks: "u" = unknown rule applied (value is the rule's default); "v" = unverified (the script caps it). No rating carries unverified true.

Conventions used (each is also a flag below):
- Own facts = the items listed under the contract in the sheet, read through each scale's wording. D2a and D2b count only this-contract or product-group items (sibling programs and shares excluded). s2 and s3 ("product or its underlying"), D6 ("this contract or a same-underlying sibling") and s1 also count sibling-tagged items about the same underlying.
- D6 "on data after 2010": a sample that runs across 2010 with no post-2010 split (the Baltussen et al. product rows, 1980s/90s to 2020) is not counted as post-2010 evidence. Out-of-sample positives on such samples score 3, not 4. A null for one pattern on such a sample does not reach 0.
- D6 in-sample evidence from multi-predictor rows counts only when a coefficient is significant at 1% or the paper's Clark-West out-of-sample test is significant. An isolated 5% coefficient with no out-of-sample support does not count.
- unknown = true only where the sheet has no bearing item and the value is the rule's default (D2a crypto; D2b satellites with leader-only programs; sat_iii with no study; rel_payout with review-site pointers only).
- Pairs: a product not listed on the modelled plan (or capped at 0) cannot be traded there, so R = 1. A is firm-wide, because the pair facts carry no automation items.

## Contracts (47 labels x 7 ratings = 329)

| Label | D2a | D2b | s1 | s2 | s3 | sat_iii | D6 | Short reasons |
|---|---|---|---|---|---|---|---|---|
| K-SGKW | 1 | 1 | 1 | 2 | 1 | 0 | 2 | Subgroup ATS 70.4%; own liquidity-provider program; mini/full pair (s1 1); EIA drift on another venue (s2 2); session jumps via sibling item; no own PD study; D6 2 like the leader |
| K-PXYN | 1 | 1 | 1 | 2 | 1 | 0 | 2 | Subgroup ATS 70.4%; IIP row only (D2b); mini/full pair; s2 2 (other venue); s3 via sibling item; D6 2 |
| K-LRVK | 1 | 1 | 1 | 2 | 1 | 0 | 2 | ATS 69.4% own; three volume-incentive programs on outrights; WTI-Brent lead-lag only at seconds, crack daily (s1 1); EIA drift only on another venue, futures evidence says absorbed (s2 2, conflicting); jumps at session open/close; leads the other venue; own D6 row null, other-venue and class positives (2) |
| K-LIRS | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | Subgroup ATS 65.7%; own market-development program; fungible (s1 1); s2 1; s3 via sibling item; no PD study (u); D6 3 via sibling |
| K-DLUC | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | Subgroup ATS 65.7%; IIP row only; ratio spread (s1 1); s2 1; s3 via sibling item; no PD study (u); D6 3 via sibling |
| K-YJXE | 1 | 1 | 1 | 1 | 1 | 0 | 3 | ATS 69.9% (HFT 31.7%); MM program names it; mechanical spreads only (s1 1); storage report absorbed in ~10 min (s2 1); settlement-window rest-of-day effect; leads look-alike and spot; Baltussen OOS 0.92% plus in-sample pre-release drift (3) |
| K-NYZZ | 1 | 1 | 2 | 2 | 1 | 0 | 3 | Subgroup ATS 67.1%; IIP row only; s1 2 and s2 2 via sibling items; fix effect via sibling; D6 3 via sibling |
| K-LGJM | 1 | 1 | 2 | 2 | 1 | 0 | 3 | ATS 67.6%; precious-metals VIP; gold-silver 1-min lead-lag (s1 2); FOMC adjustment still moving 5-10 min (s2 2); fix-window effect; leads spot; Baltussen OOS 0.08% (3) |
| K-OEVC | 1 | 1 | 2 | 2 | 1 | 0 u | 3 | Subgroup ATS 67.1%; retail rebate program plus IIP; s1/s2 via sibling items; fixing bias via sibling; no PD study (u); D6 3 via sibling |
| K-AAUT | 1 | 1 | 2 | 2 | 1 | 0 u | 3 | ATS 67.1%; precious-metals VIP; gold-silver 1-min lead-lag (s1 2); delayed macro responses (s2 2); fixing bias; no PD study (u); Baltussen OOS 1.01% (3) |
| K-SLBV | 1 | 1 | 1 | 2 | 0 | 0 | 2 | Subgroup ATS 70.0%; own market-development program; s1 1; s2 2 via sibling; s3 0; D6 2 |
| K-YBWI | 1 | 1 | 1 | 2 | 0 | 0 | 2 | ATS 70.2%; base-metals VIP; mechanical/daily only (s1 1); delayed 08:30 response (s2 2); structure only (s3 0); this venue leads; own row near-null, other-venue positive (D6 2) |
| K-OTEO | 1 | 1 | 1 | 1 | 1 | 0 | 2 | FX subgroup ATS 70.9%; FX MM program; mini/full pair (s1 1); s2 1; regional-session effect (other venue); sibling share 66.5% (sat 0); D6 2 |
| K-ASSS | 1 | 1 | 1 | 1 | 1 | 0 | 2 | ATS 82.0% (HFT 46.2%); only spread/BTIC programs plus IIP class row; mechanical (s1 1); quick FX adjustment (s2 1); regional-session effect; spot 'dominant' without a share; own D6 null (2) |
| K-QIUI | 1 | 1 | 2 | 1 | 1 | 0 | 3 | FX subgroup ATS 70.9%; FX MM program; AUD-commodity 5-min Granger (s1 2); s2 1; s3 1; D6 3 via sibling |
| K-LTAT | 1 | 1 | 2 | 1 | 1 | 0 | 3 | FX-G10 ATS 85.4%; IIP class row; AUD-commodity 5-min Granger causality (s1 2); RBA absorbed in 10 min (s2 1); regional sessions; Baltussen OOS 0.17% (3) |
| K-UQNU | 1 u | 1 | 1 | 1 | 1 | 0 u | 2 | D2a unknown (1); own MM programs; s1 1 after the evidence-rule check; s2 1; spot session effect; no PD study (u); D6 2 |
| K-JGJF | 1 u | 1 | 1 | 1 | 1 | 0 u | 2 | D2a unknown (1); own MM program 2021; mechanical (s1 1 after the evidence-rule check); volatility-only news (s2 1); spot session effect; no PD study (u); D6 2 |
| K-ZXJD | 1 u | 1 | 1 | 1 | 1 | 0 | 4 | D2a unknown (1); MM programs; s1 1; s2 1; s3 1; own IS 0.52-0.56 on 4 of 5 days (sat 0); D6 4 via sibling |
| K-OJGY | 1 u | 1 | 1 | 1 | 1 | 0 | 4 | D2a unknown (1); crypto MM program; s1 1 after the evidence-rule check; full-text macro null for the price (s2 1); spot session effect; mixed PD studies; CME ML direction study out of sample on 2020 data (4) |
| K-RISF | 1 | 1 | 2 | 1 | 1 | 0 | 3 | Index subgroup 73.7%; MM program 2019-22; s1 2 via sibling; s2 1; s3 1; ~equal PD; D6 3 via sibling |
| K-FICQ | 1 | 1 | 2 | 1 | 1 | 0 u | 3 | Index subgroup 73.7%; IIP outrights row; cross-index lead ~5 min (s1 2); s2 1; s3 1; no PD study (u); Baltussen OOS 3.15% (3) |
| K-DNXQ | 1 | 1 | 1 | 1 | 1 | 0 | 3 | Index subgroup 73.7%; MM program 2019-22; s1 1; s2 1; s3 1; ~equal PD; D6 3 via sibling |
| K-QAJV | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | ATS 81.2%; MM program to 2021-01 plus IIP; mechanical (s1 1); s2 1; s3 1; no PD study (u); Baltussen OOS 2.18% (3) |
| K-YEPF | 1 | 1 | 2 | 1 | 1 | 0 | 3 | Index subgroup 73.7%; MM program 2019-22; s1 2 via sibling; s2 1; s3 1; ~equal PD with larger sibling; D6 3 via sibling, own preprint null |
| K-KVJD | 1 | 1 | 2 | 1 | 1 | 0 | 3 | ATS 74.0%; MM program to 2021-01 plus IIP; cross-index lead 8.7-12.3 min (s1 2); drift only on a cousin (s2 1); cash-close effect; >80% own PD; Baltussen OOS 3.76% (3) |
| K-AIIW | 1 | 1 | 1 | 2 | 1 | 0 | 3 | Treasury subgroup ATS 73.1%; IIP class row; curve/calendar mechanical (s1 1); FOMC 3-hour yield drift (s2 2); New York open volatility (s3 1); Baltussen OOS 0.70% (3) |
| K-HIOT | 1 | 1 | 1 | 2 | 1 | 0 | 3 | ATS 74.0%; IIP class row; mechanical; FOMC 3-hour drift (s2 2); New York open volatility; Baltussen OOS 0.93% (3) |
| K-TATP | 1 | 1 | 1 | 2 | 1 | 0 | 3 | ATS 72.7% (HFT 45.2%); IIP class row; mechanical; FOMC 3-hour drift (s2 2); own settlement-window effect; futures lead cash; Baltussen OOS 0.86% (3) |
| K-UPOR | 1 | 1 | 1 | 2 | 1 | 0 | 3 | Treasury subgroup ATS 73.1%; IIP class row; mechanical; FOMC 3-hour drift (s2 2); New York open volatility; Baltussen OOS 0.22% (3) |
| K-JCID | 1 | 0.5 u | 1 | 2 | 1 | 0 u | 3 | Group 55.2%; leader programs only (D2b 0.5 u); s1 1; s2 2, s3 1 via sibling items; no PD study (u); D6 3 via sibling |
| K-ASNW | 1 | 0.5 u | 2 | 2 | 1 | 0 | 3 | Group 55.2%; leader programs only (0.5 u); crush via sibling (s1 2); WASDE via sibling (s2 2); volatility U-shape via sibling (s3 1); D6 3 via sibling |
| K-OMOR | 1 | 0.5 u | 1 | 1 | 0 | 0 u | 2 | Group 55.2%; leader programs only (0.5 u); s1 1; s2 1; s3 0; no PD study (u); D6 2 |
| K-GOMC | 1 | 0.5 u | 2 | 1 | 0 | 0 | 2 | Group 55.2%; leader programs only (0.5 u); crush via sibling (s1 2); s2 1; s3 0; D6 2 |
| K-WSRZ | 1 | 0.5 u | 2 | 1 | 0 | 0 | 3 | Group 55.2%; leader programs only (0.5 u); crush via sibling (s1 2); s2 1; s3 0; D6 3 via sibling |
| K-AMNJ | 1 | 1 | 1 | 2 | 1 | 0 u | 3 | Group 55.2%; IIP class row (expired own MM); s1 1; s2 2, s3 1 via sibling items; no PD study (u); D6 3 via sibling |
| K-BMTO | 1 | 1 | 2 | 2 | 1 | 0 | 3 | Group 55.2%; IIP class row; crush via sibling (s1 2); WASDE via sibling (s2 2); s3 1 via sibling; D6 3 via sibling |
| K-CSTX | 1 | 1 | 1 | 1 | 0 | 0 u | 2 | Group 55.2%; IIP class row; s1 1; s2 1; s3 0; no PD study (u); D6 2 |
| K-OQCY | 1 | 1 | 1 | 2 | 1 | 0 u | 3 | ATS 52.5% (HFT 23.9%); extended-hours MM program; calendar intraday cointegration (s1 1); WASDE reaction growing to 30 min (s2 2); settlement-window reversals; no PD study (u); own row in sample plus tiny Clark-West OOS (3) |
| K-IXHJ | 1 | 1 | 2 | 2 | 1 | 0 | 3 | ATS 53.3% (HFT 36.0%); extended-hours MM program; crush 1-min cointegration (s1 2); WASDE drift to the close (s2 2); U-shaped volatility (s3 1); no fixed leader; first-half-hour reversal, Clark-West OOS at 5% (3) |
| K-AJZH | 1 | 1 | 1 | 1 | 0 | 0 u | 2 | ATS 62.2% (HFT 26.6%); extended-hours MM program; mechanical/weekly (s1 1); volatility-only release item (s2 1); structure only (s3 0); no PD study (u); own row null (D6 2) |
| K-ODAS | 1 | 1 | 2 | 1 | 0 | 0 | 2 | Group 55.2%; extended-hours MM program; crush 1-min cointegration (s1 2); schedule and pointers only (s2 1); s3 0; own row null (D6 2) |
| K-KQRO | 1 | 1 | 2 | 1 | 0 | 0 | 3 | Group 55.2%; extended-hours MM program; crush cointegration (s1 2); s2 1; s3 0; mid-day predictor in sample with Clark-West OOS (3) |
| K-EXGX | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | Treasury subgroup 73.1% (listed from 2021); yield MM program; design relationship only (s1 1); fast absorption (s2 1); New York open volatility (s3 1); no PD study (u); D6 3 via sibling-tagged Treasury row |
| K-DCJJ | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | As K-EXGX: subgroup 73.1%; yield MM program; s1 1; s2 1; s3 1; no PD study (u); D6 3 via sibling-tagged row |
| K-NUPE | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | As K-EXGX, with outright quoting obligations in the yield MM program; no PD study found (u); D6 3 via sibling-tagged row |
| K-LWIK | 1 | 1 | 1 | 1 | 1 | 0 u | 3 | As K-EXGX: subgroup 73.1%; yield MM program; s1 1; s2 1; s3 1; no PD study (u); D6 3 via sibling-tagged row |

## Pairs (235 labels x 2 ratings = 470)

A per firm (same for all 47 pairs of the firm):

| Firm | A | Short reason |
|---|---|---|
| V-FRQI | 3 | Firm's own API explicitly allowed in evaluation and funded; HFT ban and SIM-exploitation examples (seconds-long, hundreds of trades) met; rate limit is the API's technical limit; undefined 'any short term ... trades' manipulation example; live-stage API ban outside the modelled stages |
| V-PCDG | 2 | Automation permitted firm-wide; no firm API; only through named third-party platforms; microscalping (<=5 s) and qualitative HFT rules met |
| V-PCAN | 2 | Own non-HFT bots allowed; the named platform's API is live-stage only (none in evaluation or sim funded); automation only via named platforms; 10-s hold gate met |
| V-CXFO | 2 | Automation allowed if not exploiting sim fills; no firm API, accounts on a named third-party platform (API enablement unverified); HFT ban undefined |
| V-OJVP | 2 | User-built bots allowed; API only via a named platform through an approved third-party API ($100/month); third-party algorithms need approval; undefined 'scalping algorithms' ban |

R per pair (A column repeats the firm value):

| Pair | R | A | Short reason (R) |
|---|---|---|---|
| V-FRQI|K-SGKW | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-PXYN | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-LRVK | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-LIRS | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-DLUC | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-YJXE | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-NYZZ | 4 | 3 | Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; oth... |
| V-FRQI|K-LGJM | 3 | 3 | No new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP and PPI (evaluation and funded); usually <=2... |
| V-FRQI|K-OEVC | 4 | 3 | Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; oth... |
| V-FRQI|K-AAUT | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded; 50K volatility cap 0 c... |
| V-FRQI|K-SLBV | 4 | 3 | Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; oth... |
| V-FRQI|K-YBWI | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded; 50K volatility cap 0 c... |
| V-FRQI|K-OTEO | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-ASSS | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-QIUI | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-LTAT | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-UQNU | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-JGJF | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-ZXJD | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-OJGY | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-RISF | 4 | 3 | Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; oth... |
| V-FRQI|K-FICQ | 3 | 3 | No new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP and PPI (evaluation and funded); usually <=2... |
| V-FRQI|K-DNXQ | 4 | 3 | Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; oth... |
| V-FRQI|K-QAJV | 3 | 3 | No new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP and PPI (evaluation and funded); usually <=2... |
| V-FRQI|K-YEPF | 4 | 3 | Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; oth... |
| V-FRQI|K-KVJD | 3 | 3 | No new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP and PPI (evaluation and funded); usually <=2... |
| V-FRQI|K-EXGX | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-DCJJ | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-NUPE | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-LWIK | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-AIIW | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-HIOT | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-TATP | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-UPOR | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-JCID | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-ASNW | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-OMOR | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-GOMC | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-WSRZ | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-AMNJ | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-BMTO | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-CSTX | 1 | 3 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-FRQI|K-OQCY | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-IXHJ | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-AJZH | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-ODAS | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-FRQI|K-KQRO | 4 | 3 | Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide |
| V-PCDG|K-SGKW | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-PXYN | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-LRVK | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-LIRS | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-DLUC | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-YJXE | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-NYZZ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-LGJM | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-OEVC | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-AAUT | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-SLBV | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-YBWI | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-OTEO | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-ASSS | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-QIUI | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-LTAT | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-UQNU | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-JGJF | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-ZXJD | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-OJGY | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-RISF | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-FICQ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-DNXQ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-QAJV | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-YEPF | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-KVJD | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-EXGX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-DCJJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-NUPE | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-LWIK | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-AIIW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-HIOT | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-TATP | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-UPOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-JCID | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-ASNW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-OMOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-GOMC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-WSRZ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-AMNJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-BMTO | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-CSTX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCDG|K-OQCY | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-IXHJ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-AJZH | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-ODAS | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCDG|K-KQRO | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-SGKW | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-PXYN | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-LRVK | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-LIRS | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-DLUC | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-YJXE | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-NYZZ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-LGJM | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-OEVC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-AAUT | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-SLBV | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-YBWI | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-OTEO | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-ASSS | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-QIUI | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-LTAT | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-UQNU | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-JGJF | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-ZXJD | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-OJGY | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-RISF | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-FICQ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-DNXQ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-QAJV | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-YEPF | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-KVJD | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-EXGX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-DCJJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-NUPE | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-LWIK | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-AIIW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-HIOT | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-TATP | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-UPOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-JCID | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-ASNW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-OMOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-GOMC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-WSRZ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-AMNJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-BMTO | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-CSTX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-PCAN|K-OQCY | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-IXHJ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-AJZH | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-ODAS | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-PCAN|K-KQRO | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-CXFO|K-SGKW | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-PXYN | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-LRVK | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-LIRS | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-DLUC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded; product restricted fro... |
| V-CXFO|K-YJXE | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded; product restricted fro... |
| V-CXFO|K-NYZZ | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-LGJM | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-OEVC | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-AAUT | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded; product restricted fro... |
| V-CXFO|K-SLBV | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-YBWI | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded; product restricted fro... |
| V-CXFO|K-OTEO | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-ASSS | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-QIUI | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-LTAT | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-UQNU | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-JGJF | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-ZXJD | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-OJGY | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-RISF | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-FICQ | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-DNXQ | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-QAJV | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-YEPF | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-KVJD | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-EXGX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-DCJJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-NUPE | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-LWIK | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-AIIW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-HIOT | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-TATP | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-UPOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-JCID | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-ASNW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-OMOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-GOMC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-WSRZ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-AMNJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-BMTO | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-CSTX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-CXFO|K-OQCY | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-IXHJ | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-AJZH | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-ODAS | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-CXFO|K-KQRO | 4 | 2 | Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news... |
| V-OJVP|K-SGKW | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-PXYN | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-LRVK | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-LIRS | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-DLUC | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-YJXE | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-NYZZ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-LGJM | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-OEVC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-AAUT | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-SLBV | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-YBWI | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-OTEO | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-ASSS | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-QIUI | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-LTAT | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-UQNU | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-JGJF | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-ZXJD | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-OJGY | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-RISF | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-FICQ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-DNXQ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-QAJV | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-YEPF | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-KVJD | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-EXGX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-DCJJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-NUPE | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-LWIK | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-AIIW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-HIOT | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-TATP | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-UPOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-JCID | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-ASNW | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-OMOR | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-GOMC | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-WSRZ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-AMNJ | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-BMTO | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-CSTX | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-OQCY | 1 | 2 | Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded |
| V-OJVP|K-IXHJ | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-AJZH | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-ODAS | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |
| V-OJVP|K-KQRO | 4 | 2 | Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide |

## Firms (5 labels x 4 ratings = 20)

| Firm | rel_age | rel_payout | rel_rules | rel_regulatory | Short reasons |
|---|---|---|---|---|---|
| V-FRQI | 0 | 1 | 1 | 0 | Founded 2010; open pro se court complaint (2026-04) alleging payout blocking; payout-cap cut and platform cut (dates after Sep/Oct 2025 observations); no regulatory action found |
| V-PCDG | 1 | 0 u | 1 | 0 | Operating since 2025 (<2 years); payout complaints only on review sites; split cut 100% -> 90/10 and fee rises in window; none found |
| V-PCAN | 0 | 0 u | 0 | 0 | Site since <=2022-12; review-site pointers only; one clearly material adverse change in window (another plan's target), payout-balance change dated outside it; none found |
| V-CXFO | 0 | 0 u | 1 | 0 | Since 2023; pointers only, payout page states fast approval; fee rise, five product restrictions, micro cap, inactivity closure in window; none found |
| V-OJVP | 0 | 0 u | 1 | 0 | Since <=2021-06; flipping-denial reports unverified (pointers); automation narrowing, account cap cut, split tier removed, payout cap added; none found |

## Flags for the lead

Gates: none. No pair has A = 0; no fact forbids the strategy (<=20 round trips, holds >= 5 min) at any firm.

Binary scales (D2a, s3, sat_iii, rel_*) sit on a boundary by construction. The flags below cover ratings whose evidence is near the threshold, conflicting, or open to a different reading. Each gives the alternative value.

### Global reading choices
- Rater name: the brief's template says "BlindScorer-OpusXHigh"; the JSON uses "BlindScorer2-OpusXHigh", the name this run was given.
- Sibling-tagged items for s1/s2/s3. Under a this-contract-only reading these drop: s1 2 -> 1 for K-NYZZ, K-OEVC, K-RISF, K-YEPF, K-ASNW, K-GOMC, K-WSRZ, K-BMTO; s2 2 -> 1 for K-NYZZ, K-OEVC, K-SLBV, K-JCID, K-ASNW, K-AMNJ, K-BMTO; s3 1 -> 0 for K-SGKW, K-PXYN, K-LIRS, K-DLUC, K-NYZZ, K-OEVC, K-JCID, K-ASNW, K-AMNJ, K-BMTO.
- D6 spanning samples. If a sample running to 2020 counts as "data after 2010", every D6 = 3 resting on a Baltussen out-of-sample row becomes 4: K-YJXE, K-LIRS, K-DLUC, K-LGJM, K-NYZZ, K-AAUT, K-OEVC, K-LTAT, K-QIUI, K-KVJD, K-YEPF, K-FICQ, K-RISF, K-QAJV, K-DNXQ, K-AIIW, K-HIOT, K-TATP, K-UPOR, K-EXGX, K-DCJJ, K-NUPE, K-LWIK, K-OQCY, K-JCID, K-AMNJ, K-IXHJ, K-ASNW, K-BMTO, K-KQRO, K-WSRZ. The own-contract nulls would then give D6 0 (from 2) for K-LRVK, K-ASSS, K-AJZH, K-ODAS (one tested pattern each).
- D6 in-sample threshold: K-YBWI and K-SLBV are 2 (alt 3: a 5%-level first-half-hour coefficient, t 1.97, with negative OOS R2). K-IXHJ, K-ASNW, K-BMTO, K-KQRO and K-WSRZ are 3 (alt 2: the reader labelled these rows negative; the 3 rests on secondary predictors plus Clark-West significance with negative R2_OOS).
- Unlisted pairs: R = 1 for all 109 pairs with listed_on_modelled_plan false. If the script applies listing as its own gate, the stated restrictions alone give R = 4, except R = 1 for these six: V-FRQI|K-AAUT and V-FRQI|K-YBWI (50K cap 0), and V-CXFO|K-AAUT, V-CXFO|K-YBWI, V-CXFO|K-YJXE, V-CXFO|K-DLUC (restricted products). Each alternative is in work/blind2/r_pairs_alts.json.

### Contracts
- D2a near the 50% line: K-OQCY 52.5% and K-IXHJ 53.3% (2016-18 ATS share; earlier periods and HFT shares are below 50%); the grain group siblings rest on a 55.2% subgroup share. Alt 0 for each if the narrower HFT share or the prior period governed.
- D2a conflicting facts: an ATS share of 50% or more sits beside an HFT share below 50% for K-YJXE (31.7%), K-LGJM (48.1%), K-ASSS (46.2%), K-TATP (45.2%), K-AJZH (26.6%), K-OQCY (23.9%) and K-IXHJ (36.0%). I gave 1 because "a published automated-trading or HFT share of at least 50% exists". Alt 0 if the most recent figure governs.
- D2a crypto (K-UQNU, K-JGJF, K-ZXJD, K-OJGY): no figure at all; the unknown rule gives 1.
- D2b counted the International Incentive Program (fee discounts with a volume floor, 2011-2026) as a volume-incentive program. For K-PXYN, K-DLUC, K-NYZZ, K-ASSS, K-LTAT, K-FICQ, K-AIIW, K-HIOT, K-TATP, K-UPOR, K-AMNJ, K-BMTO and K-CSTX it is the only basis. Alt 0.5 if it does not count.
- D2b K-QAJV and K-KVJD: the outright MM program was in force only to 2021-01-31 (overstrike reading); the IIP class row also applies. Alt 0.5 if neither counts.
- D2b unknown 0.5 for K-JCID, K-ASNW, K-OMOR, K-GOMC, K-WSRZ (only the leader's programs are sourced). Alt 1 if the leader program applies, which the script's link handles.
- s1 K-LRVK, K-SGKW, K-PXYN = 1. Alt 2 if the WTI-Brent lead-lag ("fully reflecting new information within minutes", 1-second data) counts as a horizon of a minute or more.
- s1 K-YJXE, K-LIRS, K-DLUC = 1. Alt 2 if the gas-crude volatility causality at 10-min intervals, or the cross-product inventory response, counts as an economic lead-lag.
- s1 K-QIUI, K-LTAT = 2, resting on a spot AUD-commodity 5-min Granger study (2000-2009, in sample, working paper) that conflicts with a daily no-causality result on futures. Alt 1.
- s1 K-KVJD, K-FICQ (and siblings K-YEPF, K-RISF) = 2, resting on a preprint's 60-min chart-extrema lead of about 5-12 min, not a return regression. Alt 1.
- s1 crypto (K-UQNU, K-JGJF, K-ZXJD, K-OJGY): the minute-level cross-asset lead-lag that would give 2 is abstract-only. The full-text items alone give 1, the cap, so 1 is reported with unverified false.
- s1 K-EXGX, K-DCJJ, K-NUPE, K-LWIK = 1. The only item is a reused full-text fact with no quote. Alt 0 if treated as unsourced.
- s2 crude (K-LRVK, K-SGKW, K-PXYN) = 2, resting on a full-text other-venue (USO) finding of slow adjustment to the day's end. Conflicting full-text futures evidence says absorption within [-5,+10] min and no predictability after 10:35, and the effect was absent in 2014-16. Alt 1.
- s2 K-YBWI, K-SLBV = 2 (copper "somewhat delayed response", delay not sized); K-AAUT, K-OEVC = 2 (delayed peaks; authors call the metals efficient). Alt 1.
- s2 equity (K-KVJD, K-FICQ, K-QAJV, K-RISF, K-YEPF, K-DNXQ) = 1. Continuing 10-30 min adjustment is documented only on a cousin index future. Alt 2 if cousin evidence counts.
- s2 K-EXGX, K-DCJJ, K-NUPE, K-LWIK = 1. Their lists lack the FOMC 3-hour yield-drift item that gives the Treasury contracts 2. Alt 2.
- s2 K-OQCY, K-IXHJ and grain siblings = 2, resting on a working paper (WASDE reaction growing after 30 min). Conflicting: two other studies find no systematic under- or overreaction. Alt 1.
- s2 crypto = 1: volatility responses are in abstracts only; full text finds no price response for bitcoin within 25-55 min. Alt 0. K-ODAS, K-KQRO, K-GOMC, K-WSRZ = 1 on a USDA schedule plus snippet pointers. Alt 0.
- s3 = 1 on volatility, jump or volume handoff effects only: K-LRVK, K-SGKW, K-PXYN, K-IXHJ, K-ASNW, K-BMTO, K-AIIW, K-HIOT, K-UPOR, K-EXGX, K-DCJJ, K-NUPE, K-LWIK. Alt 0 if s3 needs a directional effect.
- s3 crypto = 1 on a spot study whose session is defined by the futures break; the futures moved to 24/7 from 2026-05-29. Alt 0.
- s3 = 0 for K-YBWI, K-SLBV (alt 1: group-level regional volume pattern) and for K-AJZH, K-OMOR, K-CSTX, K-ODAS, K-KQRO, K-GOMC, K-WSRZ (alt 1: same session pause as corn and soybeans, where effects are documented).
- sat_iii K-ZXJD = 0. Spot held 84-87% on one of five study days; 0.52-0.56 for the futures on the other four. Alt 1 if one day suffices. K-ASSS and K-OTEO = 0: spot "dominant" with no share number. Alt 1 if "dominant" means 75% or more.
- D6 K-OJGY, K-ZXJD = 4, resting on one peer-reviewed full-text study (CME 2020 minute data, 8 months, about 54% hold-out accuracy, gross). Alt 3.
- D6 K-YEPF = 3 (sibling OOS row); K-YEPF's own full-text preprint finds 14 signal families fail net of friction in 2021-25. Alt 0.
- D6 K-YJXE, K-LIRS, K-DLUC = 3; one full-text peer-reviewed pattern (storage-day short) is insignificant and net-negative after 2011. Alt 0 if that counts as "arbitraged away".
- D6 K-EXGX, K-DCJJ, K-NUPE, K-LWIK = 3 via rows tagged same-underlying sibling. The reader notes these are not price-transfer siblings ("scorer decides"). Alt 2.
- D6 K-LGJM, K-AAUT, K-YBWI: an overreaction study on these contracts (Covid sample) defines its turning points ex post, so I did not count it. Alt 3 for K-YBWI if counted.

### Pairs
- V-FRQI|K-FICQ, V-FRQI|K-QAJV, V-FRQI|K-KVJD, V-FRQI|K-LGJM: R = 3 (5-min no-new-opens windows around CPI, FOMC decision, FOMC press conference, NFP, PPI). Alt 2 or 1: some weeks hold more than 2 windows.
- V-FRQI|K-RISF, |K-DNXQ, |K-YEPF, |K-NYZZ, |K-OEVC, |K-SLBV: R = 4 (Tier 1 window caps size; one lot still allowed). Alt 3.
- V-CXFO listed pairs: R = 4. The firm's pages conflict: plan P1 is an "unrestricted account", but a general bullet says no positions or orders 2 min around any data release. Alt 3, or 1 for K-SGKW, K-PXYN, K-LRVK and the five listed grains (weekly EIA/agricultural reports plus Tier 1 macro).
- Listed crypto pairs (V-FRQI, V-CXFO, V-OJVP with K-UQNU and K-ZXJD): R = 4. Alt 1 if firm-wide weekday-only hours count against the 24/7 exchange hours (about a third excluded since 2026-05-29).
- A V-FRQI = 3. Alt 2: the terms cite "any short term or high frequency trades" as manipulation, undefined. Its live-stage API ban binds only the live stage, outside the modelled evaluation and funded stages.
- A V-PCDG and V-CXFO = 2. Alt 3 if automation on third-party platforms counts as "API explicitly allowed".
- A V-PCAN = 2. Alt 1: the named API is explicitly unavailable in evaluation and sim funded.
- A V-OJVP = 2. Alt 3 if the approved third-party API counts as an explicit API route.

### Firms
- V-FRQI rel_payout = 1, resting on one open pro se complaint (an allegation). Alt 0.
- V-FRQI rel_rules = 1. The change dates are not stated, only that the old rules were seen in Sep/Oct 2025, so they could predate the 12-month window. Alt 0.
- V-PCDG rel_rules = 1: split cut plus fee rises. Alt 0 if fee increases are not rule changes.
- V-PCDG, V-PCAN, V-CXFO, V-OJVP rel_payout = 0 unknown: review-site pointers only. Alt 1 for V-OJVP and V-PCDG if pointer-level denial reports count.
- V-PCAN rel_age = 0. Alt 1 if the futures program launched in 2024 (pointer) after 2024-10-21.
- V-PCAN rel_rules = 0. Alt 1 if the ~3% price rise, reset-fee rises on other sizes or the VPS clause (content unknown) count as a second material adverse change.
- rel_regulatory = 0 for all five rests on search-negative results (NFA BASIC not read).
