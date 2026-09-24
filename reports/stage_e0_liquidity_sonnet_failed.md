# Stage E.0 — Liquidity census (contract specs, ADV, OI)

Run by: LiquidityCensus-SonnetMed
Run time: 2026-09-23 20:20 PDT (America/Vancouver)

## Method note (read before using any figure below)

`cmegroup.com` blocked automated fetches during this run — both `WebFetch` and a
direct `curl` returned CME's IP-block JSON message citing its Data Terms of
Use. The Wayback Machine route specified in the brief (`web.archive.org`) is
also unreachable from this session's `WebFetch` tool ("unable to fetch").
`firecrawl_scrape` was not tried (not loaded; could be tried by a follow-up
worker). As a result, every figure below was gathered through `WebSearch`,
which returns an AI-synthesized answer plus a source-link list, not a raw
page fetch. Each row cites the URL the search attributed the figure to, but
none of those pages were independently re-opened and read end-to-end by this
worker. Tick sizes and contract units are high-confidence: they are stable,
long-published figures that were repeated consistently across independent
broker/aggregator mirrors. ADV and OI are lower-confidence: most of what
turned up is asset-class-level (e.g. "Equity Index ADV") or single
headline-product mentions in CME's August 2026 monthly volume release and its
January 2026 full-year-2025 release, not a clean per-symbol series. **Nothing
here should be treated as a full-year 2025 ADV for a specific symbol unless
the period column says so explicitly** — most of what's available is the
August 2026 monthly figure, cited only because it was the newest granular
number this method could reach.

The full machine-readable version with row counts is at
`reports/stage_e0_liquidity.json`. Totals: 50/50 products have a contract
name and exchange; 45/50 have a contract unit; 43/50 have some form of tick
size/value (several flagged as unverified or ambiguous); 9/50 have any ADV
figure (all but one are single-month, not full-year); 0/50 have a clean
single-product open interest figure (one crypto entry has a combined
two-product OI number, flagged as such).

---

## K1 — Equity index (ES, NQ, RTY, YM, MNQ, M2K, MYM, NKD)

| Symbol | Exchange | Name | Unit | Tick size | Tick value | Listed | ADV | OI |
|---|---|---|---|---|---|---|---|---|
| ES | CME | E-mini S&P 500 | $50 x index | 0.25 pts | $12.50 | — | not found | not found |
| NQ | CME | E-mini Nasdaq-100 | $20 x index | 0.25 pts | $5.00 (unverified — not fetched from a primary spec page) | — | not found | not found |
| RTY | CME | E-mini Russell 2000 | $50 x index | 0.10 pts | $5.00 | — | not found | not found |
| YM | CBOT | E-mini Dow ($5) | $5 x index | 1 pt | $5.00 | — | not found | not found |
| MNQ | CME | Micro E-mini Nasdaq-100 | $2 x index | 0.25 pts | $0.50 | 2019-05-06 | 1.6M contracts, **FY2025 (record annual)** [unverified — via search synthesis, not opened at source] | not found |
| M2K | CME | Micro E-mini Russell 2000 | $5 x index | 0.10 pts | $0.50 | 2019-05-06 | not found | not found |
| MYM | CBOT | Micro E-mini Dow | $0.50 x index | 1 pt | $0.50 | 2019-05-06 | not found | not found |
| NKD | CME | Nikkei 225 (Dollar) | US$5 x index | 5 pts | $25.00 | not found | not found | not found |

Cluster-level only: CME Equity Index ADV full year 2025 = 7.4 million
contracts, +8% YoY (all equity-index products combined, source: CME
full-year 2025 release).

## K2 — Rates (ZT, ZF, ZN, TN, ZB, UB)

| Symbol | Name | Unit | Tick size | Tick value | ADV | OI |
|---|---|---|---|---|---|---|
| ZT | 2-Year T-Note | $200,000 face | 1/4 of 1/32 pt | **conflicting figures found — flagged, not resolved by this worker** | 1.9M contracts, Aug 2026 monthly (+25% YoY) | not found |
| ZF | 5-Year T-Note | $100,000 face | 1/4 of 1/32 pt | $7.8125 | not found | not found |
| ZN | 10-Year T-Note | $100,000 face | 1/2 of 1/32 pt | $15.625 | 3.1M contracts, Aug 2026 monthly (+20% YoY) | not found |
| TN | Ultra 10-Year T-Note | $100,000 face | 1/2 of 1/32 pt | $15.625 | not found | not found |
| ZB | 30-Year T-Bond | $100,000 face | 1/32 pt | $31.25 | 852,000 contracts, Aug 2026 monthly (+37% YoY) | not found |
| UB | Ultra T-Bond | $100,000 face | 1/32 pt | $31.25 | 791,000 contracts, Aug 2026 monthly, record | not found |

Cluster-level: 2025 full-year U.S. Treasury futures+options ADV = 8.3 million
contracts, record (bundles all six of the above plus options). ZT's tick
value is unresolved: one part of the search synthesis stated "1/8 of 1/32 ...
$7.8125" for ZT alongside ZF, another stated "1/32 equals $62.50 per
contract" for the 2-Year specifically. Both cannot be right for the same
tick unit; the lead should get this confirmed from a primary CME spec-page
fetch (e.g. via Firecrawl) before using it.

## K3 — FX (6A, 6B, 6C, 6E, 6J, 6S, 6M, 6N, E7, M6E, M6A, M6B)

| Symbol | Name | Unit | Tick size | Tick value | Listed | ADV | OI |
|---|---|---|---|---|---|---|---|
| 6A | Australian Dollar | 100,000 AUD | 0.0001 | $10.00 | — | not found | not found |
| 6B | British Pound | 62,500 GBP | 0.0001 | $6.25 | — | not found | not found |
| 6C | Canadian Dollar | 100,000 CAD | 0.00005 | $5.00 (derived, not stated directly) | — | not found | not found |
| 6E | Euro FX | 125,000 EUR | 0.00005 | $6.25 | — | not found | not found |
| 6J | Japanese Yen | 12,500,000 JPY | 0.0000005 | $6.25 | — | not found | not found |
| 6S | Swiss Franc | 125,000 CHF | 0.0001 | $12.50 | — | not found | not found |
| 6M | Mexican Peso | **not found** | not found | not found | — | not found | not found |
| 6N | New Zealand Dollar | 125,000 NZD | 0.0001 | $10.00 | — | not found | not found |
| E7 | E-mini Euro FX | 62,500 EUR | not found | not found | not found | not found | not found |
| M6E | E-micro Euro FX | 12,500 EUR | 0.0001 (implied) | $1.25 | 2009-03-23 | not found | not found |
| M6A | E-micro Australian Dollar | 10,000 AUD | not found | not found | 2009-03-23 | not found | not found |
| M6B | E-micro British Pound | 6,250 GBP | not found | not found | 2009-03-23 | not found | not found |

6M returned zero hits across two joint FX search passes; it was not
mentioned by any of the sources found for the other eleven FX symbols.
Cluster-level: FX ADV Aug 2026 = 730,000 contracts (all FX products
combined).

## K4 — Energy (CL, QM, MCL, NG, QG, MNG, RB, HO)

| Symbol | Exchange | Name | Unit | Tick size | Tick value | Listed | ADV | OI |
|---|---|---|---|---|---|---|---|---|
| CL | NYMEX | WTI Crude Oil | 1,000 bbl | $0.01/bbl | $10.00 | — | not found isolated (cluster: 2.3M contracts Aug 2026, likely bundles CL+QM+MCL) | not found |
| QM | NYMEX | E-mini Crude Oil | 500 bbl | $0.025/bbl | $12.50 | — | not found | not found |
| MCL | NYMEX | Micro WTI Crude Oil | 100 bbl | $0.01/bbl | $1.00 | 2021 (exact date not found) | 152,000 contracts, Aug 2026 monthly (+189% YoY) | not found |
| NG | NYMEX | Henry Hub Natural Gas | 10,000 MMBtu | $0.001/MMBtu | $10.00 | — | not found | not found |
| QG | NYMEX | E-mini Natural Gas | 2,500 MMBtu | $0.005/MMBtu | $12.50 | — | not found | not found |
| MNG | NYMEX | Micro Henry Hub Natural Gas | 1,000 MMBtu | not found | not found | 2023-11-06 | not found | not found |
| RB | NYMEX | RBOB Gasoline | 42,000 gal | $0.0001/gal | $4.20 | — | not found | not found |
| HO | NYMEX | NY Harbor ULSD (Heating Oil) | 42,000 gal | $0.0001/gal | $4.20 | — | not found | not found |

## K5 — Metals (GC, MGC, SI, SIL, HG, MHG, PL)

| Symbol | Exchange | Name | Unit | Tick size | Tick value | ADV | OI |
|---|---|---|---|---|---|---|---|
| GC | COMEX | Gold | 100 troy oz | $0.10/oz | $10.00 | not found | not found |
| MGC | COMEX | Micro Gold | 10 troy oz | $0.10/oz | $1.00 | 345,000 contracts, Aug 2026 monthly (+81% YoY) | not found |
| SI | COMEX | Silver | 5,000 troy oz | $0.005/oz | $25.00 | not found | not found |
| SIL | COMEX | Micro Silver | 1,000 troy oz | $0.005/oz | $5.00 | 63,000 contracts, Aug 2026 monthly (+286% YoY) | not found |
| HG | COMEX | Copper | **not found** | not found | not found | not found | not found |
| MHG | COMEX | Micro Copper | 2,500 lb | $0.0005/lb | $1.25 | not found | not found |
| PL | NYMEX | Platinum | 50 troy oz | $0.10/oz (source phrasing ambiguous, flagged) | $5.00 | not found | not found |

HG (standard-size Copper) specs were not returned by search; only Micro
Copper (MHG) specs came back despite the query naming both. This needs a
follow-up search or a direct CME spec-page fetch (Firecrawl).

## K6 — Ags and livestock (ZC, ZW, ZS, ZM, ZL, HE, LE)

| Symbol | Exchange | Name | Unit | Tick size | Tick value | ADV | OI |
|---|---|---|---|---|---|---|---|
| ZC | CBOT | Corn | 5,000 bu | 1/4 cent/bu | $12.50 | 602,000 contracts, Aug 2026 monthly (+36% YoY) | not found |
| ZW | CBOT | Chicago SRW Wheat | 5,000 bu | 1/4 cent/bu | $12.50 | 216,000 contracts, Aug 2026 monthly, record | not found |
| ZS | CBOT | Soybeans | 5,000 bu | 1/4 cent/bu | $12.50 | not found | not found |
| ZM | CBOT | Soybean Meal | 100 short tons | $0.10/ton | $10.00 | not found | not found |
| ZL | CBOT | Soybean Oil | 60,000 lb | 0.01 cent/lb | $6.00 | not found | not found |
| HE | CME | Lean Hogs | 40,000 lb | $0.00025/lb | $10.00 | not found | not found |
| LE | CME | Live Cattle | 40,000 lb | $0.00025/lb | $10.00 | not found | not found |

Cluster-level: Agricultural ADV full year 2025 = 1.9 million contracts,
record.

## K7 — Crypto (MBT, MET)

| Symbol | Name | Unit | Tick size | Tick value | Listed | ADV | OI |
|---|---|---|---|---|---|---|---|
| MBT | Micro Bitcoin | 0.1 BTC | $5.00/BTC (⇒ $0.50/contract) | $0.50 | 2021-05-03 | 80,000 contracts, Oct 2025 monthly (+60% YoY) | not found isolated |
| MET | Micro Ether | 0.1 ETH | 0.5 index pt | $0.05 | 2021-12-06 | not found isolated | 545,000 contracts (combined with standard ETH), as of 2025-11-28, all-time record |

Cluster-level: Q4 2025 crypto complex (all futures+options) ADV = 378,500
contracts, average daily OI = 470,400 contracts. Neither MBT nor MET has a
clean single-product OI figure; the 545,000-contract number for MET is
explicitly a combined Ether+Micro Ether figure and must not be read as
MET-only.

---

## Not found — full list

- ES: ADV any period, OI, listing date
- NQ: ADV any period, OI (tick value itself is also flagged unverified)
- RTY: ADV any period, OI
- YM: ADV any period, OI
- MNQ: OI
- M2K: ADV any period, OI
- MYM: ADV any period, OI
- NKD: listing date, ADV any period, OI
- ZT: exact tick value (conflicting sources), OI
- ZF: ADV any period, OI
- ZN: OI, full-year 2025 ADV
- TN: ADV any period, OI
- ZB: OI, full-year 2025 ADV
- UB: OI, full-year 2025 ADV
- 6A, 6B, 6J, 6S, 6N: ADV any period, OI
- 6C: ADV any period, OI, tick value not independently confirmed (derived)
- 6M: contract unit, tick size/value, ADV, OI — no source found at all
- E7: tick size/value, listing date, ADV, OI
- M6E: ADV any period, OI
- M6A, M6B: tick size/value, ADV any period, OI
- CL: CL-isolated ADV any period, OI
- QM: ADV any period, OI
- MCL: exact listing date within 2021, OI
- NG, QG: ADV any period, OI
- MNG: tick size/value, ADV any period, OI
- RB, HO: ADV any period, OI
- GC, SI: ADV any period, OI
- MGC: listing date, OI, full-year 2025 ADV
- SIL: listing date, OI, full-year 2025 ADV
- HG: contract unit, tick size/value, ADV, OI
- MHG: listing date, ADV any period, OI
- PL: ADV any period, OI
- ZC, ZW: OI, full-year 2025 ADV
- ZS, ZM, ZL, HE, LE: ADV any period, OI
- MBT: isolated OI, full-year 2025 ADV
- MET: isolated ADV any period; isolated OI (only a combined ETH+MET figure exists)

## Anything unverified that needs the lead's attention

1. ZT tick value: two mutually inconsistent figures came back from the same
   search pass. Needs a direct primary-source read (Firecrawl or a manual
   check) before use in any calculation.
2. MNQ FY2025 ADV of 1.6M contracts: came from a WebSearch synthesis
   referencing a Nasdaq.com article about CME year-end volume, not a directly
   opened and quoted press release. Flag as [unverified].
3. NQ tick value ($5.00/tick): widely known but not confirmed by opening a
   primary spec page in this run — general market-knowledge sources only.
4. PL tick size/value: source phrasing conflated "minimum tick price of
   $5.00" with tick size vs. tick value; reported as tick_value_usd = 5.0 but
   flagged ambiguous.
5. HG (standard Copper) and 6M (Mexican Peso): zero usable data found by any
   search in this run; these need a dedicated search or direct fetch attempt,
   ideally via Firecrawl since cmegroup.com and Wayback are both blocked to
   this worker's tools.
6. Nearly all ADV figures are August 2026 or October 2025 single-month
   numbers pulled from CME's monthly volume press release, not the
   2025-full-year figure the brief prefers. Only the cluster-level (asset
   class) 2025 full-year ADV numbers were found; no single-product full-year
   2025 ADV was located except the MNQ figure flagged above as unverified.
7. Open interest: essentially no clean single-product OI figures were found
   for any of the 50 products. CME publishes this on its per-product
   `.volume.html` pages and in the daily bulletin, both under cmegroup.com,
   which is blocked to this worker's tools. A follow-up pass with Firecrawl
   or a differently-routed fetch would likely close most of this gap.
