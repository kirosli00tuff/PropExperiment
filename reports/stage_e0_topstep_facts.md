# Stage E.0 — Topstep Published Facts (verbatim extraction)

Fetched by: TopstepFacts-SonnetMed. Run window: 2026-09-23 20:14–20:35 PDT (America/Vancouver).
Method: `mcp__claude_ai_Firecrawl__firecrawl_scrape` (markdown, `maxAge:0`, live fetch) used wherever it
returned 200; `WebFetch` used as a fallback (its output is an LLM paraphrase with embedded quoted
fragments in double quotes — those embedded fragments are reproduced as given, but the surrounding
prose is WebFetch's own summary, not Topstep's text; flagged per-fact below as `[WebFetch summary,
embedded quotes verbatim]`). No login, no TopstepX/ProjectX API call, no account pages were used.

Pages read (see JSON `pages_read` for the same list with timestamps):
1. https://help.topstep.com/en/articles/8284206 (When and What Products Can I Trade?) — firecrawl, 200
2. https://help.topstep.com/en/articles/8284223 (What is the Scaling Plan?) — firecrawl, 200
3. https://help.topstep.com/en/articles/10305426 (Prohibited Trading Strategies at Topstep) — firecrawl, 200
4. https://help.topstep.com/en/articles/10431370 and .../10431370-the-do-s-and-don-ts-of-sim-fills (The Do's and Don'ts of SIM Fills) — firecrawl 404, WebFetch 404 (see F7 note)
5. https://help.topstep.com/en/articles/8765442 (Order Types, Fills, and Slippage) — firecrawl, 200
6. https://help.topstep.com/en/articles/10296582 (Prohibited Conduct) — firecrawl, 200
7. https://help.topstep.com/en/articles/8284213 (TopstepX — Commissions and Fees) — firecrawl, 200
8. https://help.topstep.com/en/articles/8284211 (Economic Releases) — firecrawl, 200
9. https://help.topstep.com/en/articles/10290170 (Professional Behavior at Topstep) — firecrawl, 200
10. https://help.topstep.com/en/articles/8284215 (Express Funded Account Parameters) — firecrawl, 200
11. https://help.topstep.com/en/articles/8284197 (Trading Combine Parameters) — firecrawl, 200
12. https://help.topstep.com/en/articles/8284233 (Topstep Payout Policy) — WebFetch only (firecrawl rate-limited, not retried)
13. https://help.topstep.com/en/articles/10490293 (Daily Loss Limit in the Trading Combine and Express Funded Account) — WebFetch only
14. https://help.topstep.com/en/articles/11187768 (TopstepX API Access) — WebFetch only
15. WebSearch queries (site:help.topstep.com) used to locate pages 12–14 and to attempt to find the SIM-fills page's live URL.

---

## F1 — Permitted Product List (help.topstep.com/en/articles/8284206)

Page title: "When and What Products Can I Trade?" Page date shown at top of article: **July 13, 2026**
(matches the planning chat's "last updated 2026-07-13"). Fetched via firecrawl, verbatim markdown.

Full permitted-products table, copied exactly as rendered (each row is a table row on the page, two
columns; `*` is Topstep's own asterisk):

**CME Equity Futures**
- E-mini S&P 500 (ES)
- Micro E-mini S&P (MES)*
- E-mini NASDAQ 100 (NQ)
- Micro E-mini NASDAQ 100 (MNQ)*
- E-mini Russell 2000 (RTY)
- Micro E-mini Russell 2000 (M2K)*
- Nikkei NKD (NKD)
- Micro Bitcoin (MBT)*
- Micro Ether (MET)*

**CME Foreign Exchange Futures**
- Australian $ (6A)
- British Pound (6B)
- Canadian $ (6C)
- Euro FX (6E)
- Japanese Yen (6J)
- Swiss Franc (6S)
- E-mini Euro FX (E7)
- Micro Euro FX (M6E)*
- Micro AUD/USD (M6A)*
- Mexican Peso (6M)*
- New Zealand $ (6N)
- Micro GBP/USD (M6B)

**CME Agricultural Futures**
- Lean Hogs (HE)
- Live Cattle (LE)

**CME NYMEX Futures**
- Crude Oil (CL)
- E-mini Crude Oil (QM)
- Natural Gas (NG)
- E-mini Natural Gas (QG)
- Micro Crude Oil (MCL)*
- RBOB Gasoline (RB)
- Heating Oil (HO)
- Platinum (PL)
- Micro Henry Hub Natural Gas (MNG)

**CME CBOT Agricultural Futures**
- Corn (ZC)
- Wheat (ZW)
- Soybeans (ZS)
- Soybean Meal (ZM)
- Soybean Oil (ZL)

**CME CBOT Equity Futures**
- Mini-DOW (YM)
- Micro Mini-DOW (MYM)*

**CME CBOT Financial/Interest Rate Futures**
- 2-Year Note (ZT)
- 5-Year Note (ZF)
- 10-Year Note (ZN)
- 10-Year Ultra-Note (TN)
- 30-Year Bond (ZB)
- Ultra-Bond (UB)

**CME COMEX Futures**
- Gold (GC)
- Silver (SI)
- Copper (HG)
- Micro Gold (MGC)*
- Micro Silver (SIL)*
- Micro Copper (MHG)

Footnote (page's own words, verbatim): "See Prohibited Conduct for restrictions on specific products
marked with an asterisk (\*)."

### F1 differences vs. the planning chat's list

Planning chat list vs. Topstep page, checked symbol-by-symbol and star-by-star:

| Item | Planning chat | Topstep page (2026-07-13) | Difference |
|---|---|---|---|
| NKD | listed, unstarred | listed, unstarred | none |
| MBT | listed under "CME crypto" group, unstarred | listed under **CME Equity Futures** group, **starred (\*)** | DIFFERS: group placement AND star status differ. Planning chat had MBT unstarred and in a separate "CME crypto" category; the page lists it inside "CME Equity Futures" and starred. |
| MET | listed under "CME crypto", unstarred | listed under **CME Equity Futures**, **starred (\*)** | DIFFERS: same as MBT — group and star status both differ. |
| "CME crypto" as its own group | present (MBT, MET) | **not present** — no separate crypto group on the current page; MBT/MET are inside CME Equity Futures | DIFFERS |
| SIL (Micro Silver) | listed, unstarred, under COMEX | listed under COMEX, **starred (\*)** | DIFFERS: star status |
| MES, MNQ, M2K, MYM, M6E, M6A, MCL, MGC | planning chat: unstarred | Topstep page: all **starred (\*)** | DIFFERS: planning chat's list has none of the standard micros starred; the current page stars MES, MNQ, M2K, MYM, M6E, M6A, MCL, MGC, MBT, MET, SIL — i.e., nearly every micro-sized product is now starred. |
| 6M (Mexican Peso) | listed, unstarred | listed, **starred (\*)** | DIFFERS |
| M6B (Micro GBP/USD) | listed | listed, **unstarred** | matches (no star on either) |
| MNG (Micro Henry Hub Natural Gas) | not in planning chat's list at all | present, unstarred | ADDED (product not in the planning chat's enumerated list) |
| HG, MHG (Copper, Micro Copper) | listed | listed | none |
| ZT, ZF, ZN, TN, ZB, UB | listed | listed | none |
| ZC, ZW, ZS, ZM, ZL | listed | listed | none |
| HE, LE | listed | listed | none |
| CL, QM, MCL, NG, QG, MNG, RB, HO, PL | listed (planning chat has these under NYMEX) | listed under CME NYMEX Futures | none in membership, MCL starred per above |
| GC, MGC, SI, SIL, HG, MHG | listed under COMEX | listed under CME COMEX Futures | none in membership; MGC and SIL starred |
| E7 | listed | listed, unstarred | none |
| 6A, 6B, 6C, 6E, 6J, 6S | listed | listed, unstarred | none |
| 6N | listed | listed, unstarred | none |

**Summary of the material differences**: the planning chat's product roster (symbols present) matches
the current page almost exactly, with one addition (MNG) and one structural change (no standalone
"CME crypto" exchange group — MBT/MET now sit inside CME Equity Futures). The star pattern differs
substantially: the planning chat treated all micros as unstarred except implicitly SIL/MBT/MET (called
out separately for special weighting, not starring); the current page stars nearly every micro-sized
contract (MES, MNQ, M2K, MYM, M6E, M6A, MCL, MGC, MBT, MET, SIL) plus 6M. This is a **DIFFERS** verdict
overall — the lead should treat every one of those newly-starred products as carrying a
product-specific restriction under Prohibited Conduct (see F2).

---

## F2 — Restrictions for starred (*) products

The F1 footnote points to the "Prohibited Conduct" article
(https://help.topstep.com/en/articles/10296582). That article (fetched verbatim, page marked "Updated
over a week ago", no specific date given) does **not** contain a per-product breakdown of restrictions
tied to each starred symbol. It lists general prohibited-conduct categories (see full quote below) but
none of them name MES, MNQ, M2K, MYM, MBT, MET, SIL, M6E, M6A, MCL, MGC, or 6M individually, and none is
described as a "product-specific restriction."

**not published**: a per-product restriction keyed to the asterisk on F1, distinct from the general
Prohibited Conduct list, could not be found on help.topstep.com/en/articles/10296582 or on any linked
page. Pages checked: 10296582 (Prohibited Conduct, full text below), 10305426 (Prohibited Trading
Strategies), 8284223 (Scaling Plan — this is where the SIL/MBT/MET *scaling weighting* rule actually
lives, see F5; it is a position-sizing rule, not a "restriction" in the Prohibited Conduct sense), and
8284206 itself. The asterisk footnote's cross-reference to "Prohibited Conduct" appears to be a general
pointer rather than a per-symbol footnote list.

Full verbatim text of Prohibited Conduct's "What Is Prohibited Conduct?" section (the only candidate
content the footnote could be pointing to):

> Possible responses to a Prohibited Conduct violation:
> - Warning
> - Deletion of the impacted trading day
> - Account Reset
> - Permanent account closure
> - Delay or denial of a Payout request
>
> Ultimately, the action Topstep takes will depend on the infractions severity and your prior history (or lack thereof).
>
> ## What Is Prohibited Conduct?
> - **Unprofessional behavior** — see Professional Behavior at Topstep
> - **Excessive purchases** of Trading Combines or Resets
> - **Price exploitation** — strategies designed to exploit errors in price display or data feed delays
> - **Disruptive practices** — including spoofing
> - **Trading outside the best bid or offer**
> - **Using an external or slow data feed** to trade
> - **Coordinated trading** — performing trades in concert with others (including unconnected accounts or third parties) to pool risk, hedge aggregate positions, or trade the same or opposite strategy simultaneously
> - **Cross-account hedging (single-user)** — holding opposite positions across multiple accounts simultaneously
> - **Trades conflicting with Topstep's Terms of Use**
> - **Unfair technology** — using software, AI, ultra-high speed systems, or mass data entry to gain an unfair advantage
> - **Trading inconsistent with real futures markets** — or in a way that creates financial risk for Topstep
> - **Chargebacks or Disputes** — filing a dispute against a payment to Topstep.
> - **Exploiting platform deficiencies** — using instruments or methods that misuse bugs, errors, or deficiencies in the platform
> - **Circumventing geographical or technical restrictions**
> - **Holding a position within 2% of a product's price lock limit**
> - **Trading on behalf of others** — including sharing incentives as part of any business arrangement
> - **Account stacking** — repeatedly hitting the Maximum Loss Limit in one account and switching to another to repeat high-risk attempts
> - **Any other conduct** that Topstep determines, at its sole discretion, is uncommercial, games the market, is not a viable strategy, or is not responsible trading
> - **Do not use a VPN.** VPNs, proxy services, TOR, geo-location obfuscation, and other identity-masking services are not permitted at Topstep.

None of these items names a specific futures symbol. **Verdict: NOT PUBLISHED as a per-symbol
restriction list.** The lead should decide whether "holding a position within 2% of a product's price
lock limit" (which links to a separate article, not fetched — out of this brief's required page list)
is the mechanism intended, since price-lock limits are inherently product-specific.

---

## F3 — TopstepX Commissions and Fees (help.topstep.com/en/articles/8284213)

Page marked "Updated today" (no calendar date given by the page itself; fetched 2026-09-23).
Firecrawl verbatim.

> **Round-Turn (RT) cost:** charged when you complete both sides of a trade. Each side (Buy or Sell) incurs half the total, also called a "per side" fee.

Round-turn cost breakdown table (verbatim):
- Exchange Fee: "Exchange fees are set by the exchange and do not include the regulatory fee. Each varies by product."
- NFA Regulatory Fee: "$0.02 round turn ($0.01 per side)"
- Commissions: "Minis $1.00 round turn ($0.50 per side)"; "Micros $.50 round turn ($0.25 per side)"

Worked examples (verbatim table):

| | ES | MES |
|---|---|---|
| NFA & Regulatory Fees | $0.02 | $0.02 |
| Exchange Fee | $2.76 | $0.70 |
| Commissions | $1.00 | $0.50 |
| **Total** | $3.78 | $1.22 |

| | GC | MGC |
|---|---|---|
| NFA & Regulatory Fees | $0.02 | $0.02 |
| Exchange Fee | $3.30 | $1.40 |
| Commissions | $1.00 | $0.50 |
| **Total** | $4.32 | $1.92 |

Verbatim notice: "⚠️ Exchange fee increase starting the October 1, 2026 trading day — The CME is
raising Exchange transaction fees on 2 products. Fees apply per side, so a round turn counts both entry
and exit. MCL: $0.50 to $0.60 per side ($1.20 round turn). MNG: $0.60 to $0.70 per side ($1.40 round
turn). That's $0.10 more per side."

Full per-product round-turn cost table (verbatim, $ = total round-turn cost):

| Product | RT cost |
|---|---|
| E-mini S&P 500 (ES) | $3.78 |
| Micro E-mini S&P 500 (MES) | $1.22 |
| E-mini NASDAQ 100 (NQ) | $3.78 |
| Micro E-mini NASDAQ 100 (MNQ) | $1.22 |
| E-mini Russell 2000 (RTY) | $3.78 |
| Micro E-mini Russell 2000 (M2K) | $1.22 |
| Nikkei (NKD) | $5.32 |
| Micro E-mini Bitcoin (MBT) | $2.82 |
| Micro E-mini Ether (MET) | $0.72 |
| Crude Oil (CL) | $4.02 |
| Micro Crude Oil (MCL) | $1.52 |
| E-mini Crude Oil (QM) | $3.42 |
| Platinum (PL) | $4.32 |
| E-mini Natural Gas (QG) | $2.02 |
| RBOB Gasoline (RB) | $4.02 |
| Heating Oil (HO) | $4.02 |
| Natural Gas (NG) | $4.22 |
| Micro Henry Hub Natural Gas (MNG) | $1.72 |
| Mini-DOW (YM) | $3.78 |
| Micro Mini-DOW (MYM) | $1.22 |
| Australian $ (6A) | $4.22 |
| Micro AUD/USD (M6A) | $1.00 |
| British Pound (6B) | $4.22 |
| Canadian $ (6C) | $4.22 |
| Euro FX (6E) | $4.22 |
| Micro EUR/USD (M6E) | $1.00 |
| Japanese Yen (6J) | $4.22 |
| Swiss Franc (6S) | $4.22 |
| E-mini Euro FX (E7) | $2.72 |
| Mexican Peso (6M) | $4.22 |
| New Zealand $ (6N) | $4.22 |
| Micro GBP/USD (M6B) | $1.00 |
| 2-Year Note (ZT) | $2.32 |
| 5-Year Note (ZF) | $2.32 |
| 10-Year Note (ZN) | $2.62 |
| 30-Year Bond (ZB) | $2.76 |
| Ultra-Bond (UB) | $2.92 |
| Ultra-Note (TN) | $2.62 |
| Gold (GC) | $4.32 |
| Micro Gold (MGC) | $1.92 |
| Silver (SI) | $4.32 |
| Micro Silver (SIL) | $2.72 |
| Copper (HG) | $4.32 |
| Micro Copper (MHG) | $1.92 |
| Lean Hogs (HE) | $5.22 |
| Live Cattle (LE) | $5.22 |
| Corn (ZC) | $5.28 |
| Wheat (ZW) | $5.28 |
| Soybean (ZS) | $5.28 |
| Soybean Meal (ZM) | $5.28 |
| Soybean Oil (ZL) | $5.28 |

---

## F4 — Trading Hours (help.topstep.com/en/articles/8284206)

Verbatim, from firecrawl markdown:

> Know what you can trade and when. Topstep is a day trading program. All positions must be closed by
> 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT. No swing trading. No Forex.

Trading Hours table (verbatim):

| Session | Hours |
|---|---|
| Sunday open | 5:00 PM CT |
| Weekday close | 3:10 PM CT |
| Weekday reopen | 5:00 PM CT |
| Friday close | 3:10 PM CT (closed till Sunday at 5:00 PM) |

> All open positions and pending orders **begin to automatically cancel** at 3:10 PM CST. Avoid opening
> new positions after 3:08 PM CT — Risk Managers begin flattening at that time. It's still your
> responsibility to be flat by 3:10 PM CT.
>
> If you're trading a product with an earlier daily close than 3:10 PM CT, you must exit before that
> product's close.

Special Trading Hours (verbatim):

> **CBOT Commodity Products** (Corn, Wheat, Soybeans, Soybean Meal, Soybean Oil):
> - Sunday–Monday: 7:00 PM – 7:45 AM CT
> - Monday–Friday: 8:30 AM – 1:20 PM CT
>
> **CME Agriculture Products** (Live Cattle, Lean Hogs):
> - Monday–Friday: 8:30 AM – 1:05 PM CT
>
> **CBOT Commodity Market Pause** (Mon–Fri): 7:45 AM – 8:30 AM CT. No orders accepted during this
> window. TopstepX™ manual lockout is not available for CBOT positions held during this time.

Holiday hours: this page does not state a holiday-hours rule. **Not published** on this page; the
planning chat's D.1f finding about Independence Day 2019–2023 12:00 CT halts was drawn from a calendar
data source, not from this Topstep help page — that is outside this brief (Topstep does not appear to
publish a generic "holiday hours" rule on 8284206; not checked further per boundary — other workers own
the calendar/holiday research).

### F4 differences vs. planning chat

| Constraint | Planning chat reading | Topstep quote | Status |
|---|---|---|---|
| Daily close | "TopstepX closes at 15:10 CT for every product" | "All positions must be closed by 3:10 PM CT every weekday" / "Weekday close: 3:10 PM CT" | **CONFIRMS** (3:10 PM CT = 15:10 CT) |
| Flattening start | "Risk Managers begin flattening at 15:08 CT" | "Avoid opening new positions after 3:08 PM CT — Risk Managers begin flattening at that time" | **CONFIRMS** (3:08 PM CT = 15:08 CT) |

---

## F5 — Position Limits, Special Weightings, Scaling Plan

### Position limits by account (help.topstep.com/en/articles/8284197, Trading Combine Parameters; page marked "Updated over 2 weeks ago")

Verbatim Maximum Position Size table:

> The maximum number of contracts you can hold open at one time, per account. Micros and minis count at a 10:1 ratio.

| Account Size | Max Contracts | Max Micros |
|---|---|---|
| $50K | 5 | 50 |
| $100K | 10 | 100 |
| $150K | 15 | 150 |

> **Hint:** You're never required to trade the maximum. Fewer contracts is always allowed.
>
> **⚠️ Please note:** The Micro to Mini ratio functionality is available for the Trading Combine and
> Express Funded Account. It is not currently available for the Live Funded Account.

This is the Trading Combine's limit table; the XFA Scaling Plan (below) reuses the same "$50K → 2-lot"
style example, so the same 10:1, mini-equivalent structure applies to XFA balances as they scale.

### Scaling Plan (help.topstep.com/en/articles/8284223, page marked "July 16, 2026"; firecrawl verbatim)

> The Scaling Plan is an Express Funded Account® (XFA) objective. It sets your Maximum Position Size —
> the max contracts you can hold at one time — based on your current account balance.
>
> ☝️ The Scaling Plan does not apply to the Live Funded Account®. It's been replaced in the Live Funded
> Account by Dynamic Live Risk Expansion.
>
> **10:1 ratio:**
> - 1 Mini = 10 Micro contracts
> - Limits are based on mini-contract equivalents
>
> Example — $50K XFA, 2-lot Scaling Plan:
> - 2 Minis, OR
> - 20 Micros, OR
> - Any combo equal to 2 Minis
>
> **→ Key rule:** Your max contracts do not increase mid-session. Hit the threshold to release more
> buying power? Wait for the next session.

Special Product Weightings table (verbatim):

| Product | Rule |
|---|---|
| Micro Silver (SIL) | 5:1 ratio vs. Silver (SI); counts as 2 of any other micro |
| Micro Bitcoin (MBT) | Capped at mini-equivalent lot sizes, not standard micro scaling |
| Micro Ether (MET) | Capped at mini-equivalent lot sizes, not standard micro scaling |

> **What if I accidentally exceed my limit but fix it right away?** Errors corrected in under 10
> seconds are ignored. Leave too many contracts on for 10+ seconds and your account may be reviewed.

**XFA scaling plan tier table** (the actual $/max-contract schedule beyond the one worked example
above): the page shows this as an embedded chart image ("XFA charts - hc.png"), not as text or an HTML
table. **Not published as extractable text** — the full tier schedule (balance thresholds → max
contracts, beyond the single "$50K → 2 lot" example) exists only as an image on this page and could not
be transcribed from the fetched markdown.

### F5 differences vs. planning chat

| Constraint | Planning chat reading | Topstep quote | Status |
|---|---|---|---|
| 50K position limit | "5 minis or 50 micros" | "$50K → 5 Max Contracts, 50 Max Micros" (Trading Combine table) | **CONFIRMS** |
| SIL weighting | not specified in prompt beyond "special weightings ... published" | "5:1 ratio vs. Silver (SI); counts as 2 of any other micro" | new verbatim fact, no prior planning-chat number to compare |
| MBT/MET weighting | not specified | "Capped at mini-equivalent lot sizes, not standard micro scaling" | new verbatim fact |
| XFA scaling tiers (full table) | not specified | image-only, not extractable as text | **NOT PUBLISHED** (as text) |

---

## F6 — News/Economic-Release Trading Rules: Combine vs. XFA

Source: help.topstep.com/en/articles/8284211 (Economic Releases; page marked "Updated over 2 weeks
ago"). Firecrawl verbatim. This page does not distinguish Combine vs. XFA — it states the rule for both
in one sentence:

> Topstep doesn't require you to flatten positions during economic releases — in SIM or Funded Accounts.
> But we highly recommend using caution or stepping aside when a release is coming up that affects your
> product.
>
> Slippage is common during these events. Orders can execute at a worse price than expected. That's not
> a bug — that's the market.
>
> A few things to know:
> - Trades impacted by economic releases are **not eligible for exceptions or Reset credits**
> - Results are your responsibility — full stop
> - To reduce slippage risk: cut your position size, use limit orders, or avoid trading the event entirely.

The only trading-behavior *restriction* tied to news anywhere in the pages read is on
10305426 (Prohibited Trading Strategies): "Trading Maximum Position Size into Major News Events —
Purposefully trading your full Maximum Position Size directly into a scheduled major news event" is
listed as a prohibited behavior (not a flatten-before-news rule; it prohibits full-size positioning
into a scheduled release).

Common Economic Releases table (verbatim):

| Release | Time (CT) | Products Affected |
|---|---|---|
| Unemployment Rate | 7:30 AM | ES, NKD, NQ, 6A, 6B, 6C, 6E, 6J, 6S, E7, GE, YM, UB, ZT, ZF, ZN, ZB, GC, RTY, SI, HG, TN, 6M, M6A, M6E, 6N, MBT, MET |
| FOMC Statement | 1:00 PM | All products |
| Crude Oil Inventories (EIA) | 9:30 AM / 10:00 AM* | CL, QM, MCL, RB |
| Natural Gas Inventories (EIA) | 9:30 AM | NG, QG |
| Crop Production | 11:00 AM | ZC, ZS, ZW, ZM, ZL |

Footnotes (verbatim): "*Pending abbreviated trading hours. Times are subject to change — Traders are
responsible for knowing what releases are scheduled and when." / "**Micro contracts also apply."

**No separate XFA-specific news-trading page exists** among the pages read or found by search; the
Economic Releases article explicitly covers "SIM or Funded Accounts" (i.e., both Combine and XFA/LFA)
in the same sentence. **Verdict: the Combine-vs-XFA distinction the brief asked to check separately is
NOT PUBLISHED as two separate rules — Topstep publishes one rule that applies to both.**

### F6 differences vs. planning chat

The planning chat's premise (a list of specifically restricted events/time-windows, or a statement that
news trading is flatly disallowed) is **not what the page says**. The page affirmatively states no
flatten requirement exists ("Topstep doesn't require you to flatten positions during economic
releases"), and the only related prohibition is the narrower "don't trade full Max Position Size into a
scheduled major news event" rule from Prohibited Trading Strategies. If the planning chat assumed a
broader news-trading restriction (e.g., a blackout window), that reading **DIFFERS** from the published
text — the lead should treat "news trading is allowed, sizing at max is not" as the current rule.

---

## F7 — Prohibited-Strategy and SIM-Fill Pages, Quoted in Full

### help.topstep.com/en/articles/10305426 — "Prohibited Trading Strategies at Topstep"

Page date shown: **June 10, 2026** (matches planning chat's "updated 2026-06-10"). Firecrawl verbatim,
full article text below:

> Topstep prohibits specific trading behaviors that exploit program structure, contradict real-market
> discipline, or create financial risk for the firm. These aren't gray areas — they're hard stops.
>
> **Account Stacking**
> Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account, then switching
> to another account and repeating. The goal is to run high-risk attempts until a large win occurs. This
> exploits risk parameters and is not permitted.
>
> **Intentionally Depleting a Live Funded Account**
> Deliberately drawing down a Live Funded Account® (LFA) balance to force a failure. Not permitted.
>
> **Violating Topstep's Terms of Use**
> Any trades performed in conflict with Topstep's Terms of Use or the Trading Combine® (TC) terms and
> conditions.
>
> **Using Unfair Technology**
> Using software, AI, ultra-high speed systems, or mass data entry that manipulates, abuses, or provides
> an unfair advantage on the platform or in the program.
>
> **Trading Outside Real Market Behavior**
> Executing trades in a way that contradicts how trading actually works in the applicable futures
> markets, or in a way that creates justified concern that Topstep may suffer financial or other harm.
>
> **Trading Outside the Best Bid or Offer**
> Placing orders at prices outside the current best bid or offer.
>
> **Trading Maximum Position Size into Major News Events**
> Purposefully trading your full Maximum Position Size directly into a scheduled major news event.
>
> ## The Do's and Don'ts of SIM Fills
>
> SIM fills aren't free money. Exploiting the simulator will get you removed from the program. Topstep
> prohibits using the simulated environment to gain an unfair edge. We retain the right to reject profit
> claims if abuse is suspected. If you're here to trade, this isn't about you.
>
> Examples of exploiting or manipulating the Topstep simulator include, but are not limited to:
> - Running scalping algorithms designed to exploit unrealistic SIM fills
> - Making hundreds of rapid trades to take advantage of preferential queue position in SIM
> - Initiating reckless trades in gapped markets to profit from stray fills — these are improbable in live markets
> - Repeatedly exploiting the relative lack of slippage in SIM to achieve impossible stop-loss execution
> - Using tight brackets or auto-breakeven to take advantage of favorable SIM fills
>
> **👉 If this doesn't sound like you, it probably isn't.**
>
> The vast majority of Traders are here to learn and build toward consistent profitability. A few lucky
> fills won't get your Payout rejected. The behaviors above are intentional and systematic — usually
> hundreds or thousands of trades per day, with average durations measured in seconds, not minutes.
>
> Topstep shuts this down quickly to keep risk managers and coaches focused on helping Traders — not
> monitoring abuse.
>
> For more information, please refer to our Prohibited Conduct and Professional Behavior policies.

**Checked phrases (all found verbatim above):**
- "Running scalping algorithms designed to exploit unrealistic SIM fills" — FOUND, verbatim.
- "Making hundreds of rapid trades to take advantage of preferential queue position in SIM" — FOUND, verbatim.
- "hundreds or thousands of trades per day, with average durations measured in seconds, not minutes" — FOUND, verbatim.
- Trading gapped markets for stray fills — FOUND, worded as "Initiating reckless trades in gapped markets to profit from stray fills — these are improbable in live markets."
- Exploiting lack of SIM slippage on stops — FOUND, worded as "Repeatedly exploiting the relative lack of slippage in SIM to achieve impossible stop-loss execution."
- Tight brackets / auto-breakeven for favourable SIM fills — FOUND, worded as "Using tight brackets or auto-breakeven to take advantage of favorable SIM fills."

### help.topstep.com/en/articles/10431370 — "The Do's and Don'ts of SIM Fills"

**Not published as a separate live page.** Both `firecrawl_scrape` (bare numeric URL, statusCode 404,
"Uh oh. That page doesn't exist.") and `WebFetch` (full slugged URL
`.../10431370-the-do-s-and-don-ts-of-sim-fills`, HTTP 404) returned 404. A WebSearch for
`site:help.topstep.com "SIM fills"` still lists a result titled "The Do's and Don'ts of SIM Fills |
Topstep Help Center" at that same article ID/slug, but fetching it directly 404s — the search engine's
index entry appears stale. The content that used to be (or is meant to be) at that URL is now, verbatim,
the "## The Do's and Don'ts of SIM Fills" section embedded inside article 10305426 (quoted in full
above) — confirmed by matching heading text and the identical bullet list. The Wayback Machine could not
be checked (WebFetch reported it cannot fetch web.archive.org in this environment). **Verdict: page
10431370 is NOT PUBLISHED as a standalone URL; its content is published as a section of 10305426.**

---

## F8 — Limit-Order Fill Rule (help.topstep.com/en/articles/8765442)

Page: "Order Types, Fills, and Slippage." Page date shown: **"Updated over a week ago"** (Intercom's
relative-date format; no calendar date given). Firecrawl verbatim.

> **Limit Order**
> Sets the worst price you'll accept. Limit buys go below current price. Limit sells go above it.
>
> Price execution over speed. Trade-off: the market has to trade _through_ your price — not just touch
> it. You might not get filled. Partial fills happen. Order stays in the book until it's filled,
> canceled, or expired.

And in the FAQ section:

> **Why wasn't my order filled?**
> Low liquidity or high volatility can make it hard to find a match at your price. Limit orders
> especially — if the market doesn't trade through your price, you don't get filled. Check time and
> sales data to see what the market was doing at the time.

### F8 differences vs. planning chat

| Constraint | Planning chat reading | Topstep quote | Status |
|---|---|---|---|
| Limit fill rule | "limit orders fill only when the market trades through the price" | "the market has to trade _through_ your price — not just touch it. You might not get filled." | **CONFIRMS** |

---

## F9 — XFA Payout Rules per Tier

Sources: help.topstep.com/en/articles/8284215 (Express Funded Account Parameters — firecrawl verbatim,
page dated **August 5, 2026**) and help.topstep.com/en/articles/8284233 (Topstep Payout Policy —
WebFetch summary with embedded quotes only, page marked "Updated over 3 weeks ago" per WebFetch) and
help.topstep.com/en/articles/10490293 (Daily Loss Limit — WebFetch summary with embedded quotes only,
page dated **June 30, 2026** per WebFetch).

### Standard vs. Consistency, at a glance (firecrawl verbatim, from 8284215)

| | XFA Standard | XFA Consistency |
|---|---|---|
| Payout eligibility | 5 winning days of $150+ | 3 days traded, 40% consistency target |
| Max Payout | 50% of balance, up to $5,000* | 50% of balance, up to $6,000* |
| Profit split | 90/10 | 90/10 |
| Scaling Plan | ✅ | ✅ |
| Maximum Loss Limit (MLL) | ✅ | ✅ |
| Daily Loss Limit (DLL) | Optional | Optional |
| Consistency Target | ❌ | ✅ |
| Profit Target | ❌ | ❌ |

Footnote (verbatim): "*See the Payout Policy for Payout cap details by account size."

Consistency formula (verbatim): "Consistency = Largest Winning Day ÷ Total Net Profit." Example
(verbatim): "Total profit $1,000, best day $400 = 40% ✅." / "Best day $450 = 45% ❌."

### Per-tier payout caps [WebFetch summary, embedded quotes verbatim] — from article 8284233

This table is a WebFetch paraphrase; the quoted fragments in double quotes below are Topstep's own
wording as WebFetch extracted them, but the table structure and any unquoted words are WebFetch's
summary, not copied directly from the page markup. **This should be independently re-verified with a
direct scrape before it enters any pre-registration or design document**, since firecrawl was
rate-limited and not retried for this page within this task.

| Tier | Path | Quoted terms |
|---|---|---|
| $50K | Standard | "5 winning days of $150+" ... "Request 50% of the account balance up to $2,000" ... "90/10 split" |
| $50K | Consistency | "3 days with 40% consistency target" ... "Request 50% of the account balance up to $3,000" ... "90/10 split" |
| $100K | Standard | "5 winning days of $150+" ... "Request 50% of the account balance up to $3,000" ... "90/10 split" |
| $100K | Consistency | "3 days with 40% consistency target" ... "Request 50% of the account balance up to $4,000" ... "90/10 split" |
| $150K | Standard | "5 winning days of $150+" ... "Request 50% of the account balance up to $5,000" ... "90/10 split" |
| $150K | Consistency | "3 days with 40% consistency target" ... "Request 50% of the account balance up to $6,000" ... "90/10 split" |

Note: the $150K Standard cap ($5,000) and $150K Consistency cap ($6,000) as WebFetch reported them match
the "up to $5,000*" / "up to $6,000*" figures shown verbatim on 8284215's at-a-glance table, which is a
firecrawl-verified cross-check and supports the WebFetch figures for the $150K row specifically. The
$50K and $100K rows could not be cross-checked against firecrawl-verified text within this task.

### Daily Loss Limit option [WebFetch summary, embedded quotes verbatim] — from article 10490293

> Daily Loss Limit at checkout is fixed (no changes later)
> Applies to your Express Funded Account after you pass.

DLL amounts and pricing, per WebFetch's extraction:
- $50K Account: DLL amount $1,000; Responsible Trading Discount "$10 off"
- $100K Account: DLL amount $2,000; Responsible Trading Discount "$20 off"
- $150K Account: DLL amount $3,000; Responsible Trading Discount "$30 off"

WebFetch's summary of the doubling mechanism (from 8284233): 'The limited-time offering allows traders
who add a Daily Loss Limit at checkout to "unlock double per-request payout caps." The document shows
doubled caps (e.g., $50K Standard increases from $2,000 to $4,000) but does not specify the DLL cost
[on that page].' On trigger (from 10490293, quoted): "Open positions are flattened" / "No new trades
until 5 PM CT next session."

**Not fully verified**: the exact per-tier price of the DLL option ($1,000/$2,000/$3,000 above) and the
doubled payout-cap figures are WebFetch paraphrases with embedded quotes, not a firecrawl-verified raw
scrape. Flagged for independent re-check (fable xhigh per CLAUDE.md, since these are numbers that could
enter a design decision) before use in any pre-registration.

---

## F10 — API Access (help.topstep.com/en/articles/11187768, "TopstepX API Access")

[WebFetch summary, embedded quotes verbatim throughout — firecrawl was not retried for this page].
Page "Last Updated" per WebFetch: "This week" (Intercom relative date, no calendar date extracted).

> "All trading activity must originate from your personal device. The use of VPS, VPNs, and remote
> servers is prohibited by Topstep's Terms of Use."

Server/logging carve-out (verbatim per WebFetch extraction): "your server can watch and record, but it
cannot trade."

Sandbox (verbatim): "No. There is currently no sandbox environment available. To test your strategy,
use a Practice account instead — same endpoints and real-time hubs, no risk to an Evaluation account."

High-frequency trading (verbatim fragment): custom bots are permitted "subject to standard platform
rules and our prohibition on highfrequency trading (HFT)" [sic — "highfrequency" is WebFetch's
rendering; the source page's exact spacing/hyphenation was not independently confirmed].

Automated trading (verbatim): "Yes. Custom automated strategies and bots are allowed via the TopstepX /
ProjectX API, subject to standard platform rules." Responsibility (verbatim fragment): systems must
"operate within all applicable rules."

Pricing (verbatim): "API Access is $29/month. Topstep Traders get 50% off with code topstep — that's
$14.50/month, valid every month with no end date."

**Not fully verified**: this entire page's content is a WebFetch paraphrase, not a direct scrape.
Flagged for independent re-check before any pre-registration or harness code relies on the exact HFT
threshold or the personal-device rule's precise wording.

### F10 differences vs. planning chat

No specific planning-chat reading of the API personal-device/VPS rule was given in the brief to compare
against; recorded here as a new fact for the lead's use, not a confirm/differs verdict.

---

## F11 — Other Automated-Trading / Bot Statements Found

Beyond F10, two more pages state automated-trading conditions directly (both firecrawl-verbatim):

From 8284197 (Trading Combine Parameters) FAQ:
> **Can I use automated trading strategies?**
> Yes, with conditions. Topstep won't help set up or troubleshoot automated strategies, and no
> exceptions are made for errant trades or malfunctions. Test on your Practice Account first and review
> Prohibited Conduct and Prohibited Trading Strategies before going live. You can also use a trade
> copier to duplicate trades across multiple accounts.

From 8284215 (Express Funded Account Parameters) FAQ:
> **Can I use automated strategies?**
> Yes, with conditions. Topstep won't help set them up or cover malfunctions. Review Prohibited Conduct
> and Prohibited Trading Strategies first.
>
> **Can I trade across multiple XFAs at once?**
> Yes, up to $750K buying power using a trade copier. ... Hedging across accounts and coordinated
> trading with others is prohibited.

From 10296582 (Prohibited Conduct), the general "unfair technology" clause (already quoted in full in
F2) is the operative restriction on bots/AI: "Unfair technology — using software, AI, ultra-high speed
systems, or mass data entry to gain an unfair advantage."

---

## Not Published — Summary List

1. F2: a per-symbol restriction list keyed to F1's asterisks (checked: 10296582, 10305426, 8284223, 8284206).
2. F4: a generic holiday-hours rule on the trading-hours page itself (checked: 8284206 only, per boundary).
3. F5: the full XFA Scaling Plan balance-tier table beyond the single "$50K → 2 lots" example — exists only as an embedded chart image (checked: 8284223).
4. F6: a Combine-vs-XFA-specific pair of news-trading rules — only one unified rule is published (checked: 8284211, 10305426).
5. F7: help.topstep.com/en/articles/10431370 as a standalone page — 404 on both firecrawl and WebFetch; content lives inside 10305426 instead (checked: both URL forms, WebSearch).

## F12 — Lead Follow-up (curl + BeautifulSoup, verbatim; WebSearch and Firecrawl not used)

Fetched 2026-09-23 21:52–21:53 PDT via `curl -sL -A "Mozilla/5.0" <url> -o <file>.html` then
`python3 -c "...bs4...get_text('\n')..."`, all HTTP 200. Pages discovered via
`https://help.topstep.com/en/?q=<terms>` search results and via related-article links inside pages
already read (per the lead's instructions; WebSearch and Firecrawl were not called).

### F12.1 — Q1: the asterisk restriction on starred products

No page names MES, MNQ, M2K, MYM, M6E, M6A, 6M, MBT, MET, MCL, MGC, or SIL together as a single
"restricted list" the way the F1 footnote implies. Checked: 10296582 (Prohibited Conduct, re-read,
no new content), 8284225 → actual URL
`https://help.topstep.com/en/articles/8284225-staying-outside-the-2-price-limit-zone` ("Staying
Outside the 2% Price Limit Zone," page dated **May 29, 2026**), 13747047 ("Understanding Hedging,"
page dated **July 27, 2026**), and 13613539 ("Risk Adjustments: High Risk/High Volatility," page
marked "Updated this week").

The price-lock-limit page (8284225) does not single out the starred products — its only named list is
different: "Equity products ES, MES, NQ, MNQ, RTY, M2K, YM, and MYM overnight price limits have
expanded from 5% to 7%," a note about limit width, not a restriction. The Hedging page (13747047)
names MES/ES and MNQ/NQ only as an illustrative example of what cross-account hedging looks like
("Cross-account hedging means simultaneously going long and short the same or correlated instrument
across multiple accounts — such as MES/ES, MNQ/NQ"), not a per-symbol restriction either.

The one page that does name most of the starred products individually with an actual restriction is
**13613539, "Risk Adjustments: High Risk/High Volatility"** — but the restriction is conditional
(triggered only during elevated volatility) and is a position-*size* cap, not a trading prohibition.
Quoted in full, the relevant sections:

> During extreme volatility, we may temporarily tighten position limits on affected products. ...
> Micro Contract Limits[.] Mini Contract Restrictions[:] Trading on mini-sized contracts or larger may
> be temporarily halted for affected products.
>
> Current Restrictions — Trading Combine, Express Funded Account, Pro Account / Live Funded Account.
> The numbers shown use a 3-tier format: $50K / $100K / $150K.
>
> **Energies Restriction** — RBOB Gasoline (RB) = 3/6/9; Heating Oil (HO) = 3/6/9; Crude Oil (CL) =
> 3/6/9; Micro Crude Oil (MCL) = 30/60/90 [TC/XFA/Pro] or 3/6/9 [LFA]; E-Mini Crude Oil (QM) = 3/6/9.
>
> **Metals Restriction** — Gold (GC) = 3/6/9; Micro Gold (MGC) = 30/60/90 [TC/XFA/Pro] or 5/10/15
> [LFA]; Silver (SI) = 0; Micro Silver (SIL) = 2/4/6; Copper (HG) = 0; Micro Copper (MHG) = 2/4/6;
> Platinum (PL) = 0.
>
> 🧪 Labs: Restricted Products — In the $25K Static Trading Combine, restricted products are set to a
> max contract size of 1 mini/10 micros. In the $250K Trading Combine, restricted energies are set to a
> max contract size of 15 minis/150 micros. For SIL/MHG, 10 minis/100 micros. SI, HG, and PL are still
> 0. In the $3K Challenge, you cannot trade MHG, MET, MBT, or SIL. Trading during CPI is also restricted
> to 0. Additionally, MGC and MCL is limited to 6 micros. In the $1.5K Challenge, you cannot trade MHG,
> MET, MBT, or SIL. MGC/MCL are limited to 1. Trading during CPI is also restricted to 0. In the $6K
> Challenge, you cannot trade MHG, SIL, HG, SL, CL, GC, HO, QM, PL, or RB. Trading during CPI is also
> restricted to 0. Additionally, MGC and MCL is limited to 6 micros.
>
> CPI Release Restrictions — Ahead of Consumer Price Index (CPI) releases, Topstep temporarily restricts
> new opening transactions on equity index products (ES, RTY, YM, NQ, NKD) in SIM to protect Traders
> from extreme volatility. Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions
> permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after).
> Micros (MES, M2K, MYM, MNQ, MGC, SIL, MHG): Opening transactions limited to 1, 3, 6, 9, and 15
> contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window.

This names MES, M2K, MYM, MNQ, MGC, SIL, MCL, MHG, MBT, MET individually with concrete, product-specific
numeric restrictions (CPI-window caps, volatility-window caps, or outright product bans on the smallest
account tiers) — the closest verbatim match to what the F1 asterisk footnote promises, even though the
page is not itself titled "Prohibited Conduct" and the restriction is conditional/event-driven rather
than a standing rule. **6A/6M/M6A/M6E/M6B are not named anywhere in this page** — no restriction found
for those FX products under any of F2's or F12's checked pages. Plain statement: **for M6E, M6A, and
6M specifically, no product-specific restriction naming them was found on any page checked (F2 or
F12); the asterisk on those three has no located textual referent beyond the generic "See Prohibited
Conduct" pointer.**

### F12.2 — Q2: F9 and F10 upgraded to verbatim curl/bs4 text

**F9 upgrade — Payout Policy (help.topstep.com/en/articles/8284233), fetched verbatim via curl, page
marked "Updated over 3 weeks ago":**

> 2 paths. 1 goal. Express Funded Account® Standard. Express Funded Account® Consistency.
>
> Standard Path: 5 winning days of $150+. Request 50% of the account balance up to $5000*. 90/10 split.
> Consistency Path: 3 days with 40% consistency target. Request 50% of the account balance up to
> $6,000*. 90/10 split.
>
> **Payout caps by account size** — Max Payout per request: 50% of your account balance up to the cap
> below.
>
> | Account Size | XFA Standard | XFA Consistency |
> |---|---|---|
> | $50K | $2,000 | $3,000 |
> | $100K | $3,000 | $4,000 |
> | $150K | $5,000 | $6,000 |
>
> 👉 Payout caps apply to XFA accounts only. Live Funded Account Payouts are not capped.
>
> ⏰ Limited Time Offering: Add a Daily Loss Limit (DLL) at checkout in the Trading Combine, and
> increase your Payout Cap once you pass and activate an Express Funded Account. Available starting at
> 3:30 PM CT on Tuesday, June 2nd. Traders who voluntarily add a Daily Loss Limit to their account
> unlock double per-request payout caps. No DLL added = current caps remain unchanged.
>
> | Account | Path | Current Cap | With DLL (new) |
> |---|---|---|---|
> | $50K | Standard | $2,000 | $4,000 |
> | $50K | Consistency | $3,000 | $6,000 |
> | $100K | Standard | $3,000 | $6,000 |
> | $100K | Consistency | $4,000 | $8,000 |
> | $150K | Standard | $5,000 | $10,000 |
> | $150K | Consistency | $6,000 | $12,000 |
>
> If I add a DLL at checkout during Express Funded Account activation or Reactivation, will I still get
> the increased Payout cap? No. Only if you already added the DLL when you purchased your Trading
> Combine. Adding it at the XFA stage doesn't unlock the higher cap.

This replaces the earlier WebFetch paraphrase of F9.3/F9.6 with an exact, source-verified table; the
earlier paraphrase's numbers were correct.

**F9 upgrade — Daily Loss Limit page (help.topstep.com/en/articles/10490293), fetched verbatim via
curl, page dated June 30, 2026:**

> The Daily Loss Limit parameters are: $50K Account: $1,000. $100K Account: $2,000. $150K Account:
> $3,000.
>
> ⚠️ Important: Daily Loss Limit at checkout is fixed (no changes later). Applies to your Express Funded
> Account after you pass. All original account rules and objectives still apply.
>
> Responsible Trading Discount — There's now a Responsible Trading Discount when you add a DLL at
> purchase for No Activation Fee Trading Combines and Back2Funded Reactivations. No Activation Fee
> Trading Combine: $10 off → 50K, $20 off → 100K, $30 off → 150K. Back2Funded Reactivation: $50 off
> Reactivation Fees.
>
> What Happens When It Triggers — Net P&L hits or exceeds the DLL during the trading day (5 PM CT –
> 3:10 PM CT): Open positions are flattened. Pending orders are canceled. No new trades until 5 PM CT
> next session. Example: $150K Trading Combine® with a $3,000 DLL. Net P&L hits -$3,000 → auto-
> liquidated. Back at it tomorrow at 5 PM CT.
>
> The Daily Loss Limit (DLL) is optional in the Trading Combine® and Express Funded Account® (XFA).
> It's automatic in the Live Funded Account® (LFA).

This replaces the earlier WebFetch paraphrase (F9.4/F9.5) with exact text; the earlier paraphrase's
DLL dollar amounts and discount amounts were correct. New detail not previously captured: the
Responsible Trading Discount as stated here applies to "No Activation Fee Trading Combines and
Back2Funded Reactivations" — it does not mention Express Funded Account Activations in this exact
sentence (the earlier F9 markdown section had said "No Activation Fee Trading Combines, Express Funded
Account Activations, and Back2Funded Reactivations" based on a WebSearch snippet; the curl-verified
page text names only two of those three categories in this sentence — flagged as a minor discrepancy
between the WebSearch-derived text used earlier and the page's actual current wording).

**F10 upgrade — TopstepX API Access (help.topstep.com/en/articles/11187768), fetched verbatim via curl,
page marked "Updated this week":**

> VPNs, VPS, and Remote Servers — All trading activity must originate from your personal device. The
> use of VPS, VPNs, and remote servers is prohibited by Topstep's Terms of Use. Running automation on a
> VPS can result in account suspension or removal from the program.
>
> You may still use your own private server for supporting work that doesn't touch order flow:
> Allowed on a private server: Historical data storage; Research and backtesting; Logging and
> analytics; A read-only dashboard. Not allowed on a private server: Placing, modifying, or cancelling
> orders; Any automated trigger that can reach the order endpoints; Routing or relaying orders on your
> behalf; Receiving copies of your own fills, positions, and P&L [listed under "Not allowed"].
> The line is order transmission: your server can watch and record, but it cannot trade.
>
> Is there a sandbox environment for testing? No. There is currently no sandbox environment
> available. To test your strategy, use a Practice account instead — same endpoints and real-time hubs,
> no risk to an Evaluation account.
>
> Can I build and use my own custom trading bot with the TopstepX / ProjectX API? Yes. Custom automated
> strategies and bots are allowed via the TopstepX / ProjectX API, subject to standard platform rules
> and our prohibition on highfrequency trading (HFT). You're free to develop your own system without
> additional restrictions beyond those standard rules. You remain the owner of your bot and are solely
> responsible for its design, performance, and behavior — including making sure it operates within all
> applicable rules.
>
> Can I use the ProjectX API if I'm in a Live Funded Account? No, Live funded accounts are not allowed
> to trade through the ProjectX API. The API Gateway is built for the simulated environment and isn't
> available on Live.
>
> Cost and Billing — API Access is $29/month. Topstep Traders get 50% off with code topstep — that's
> $14.50/month, valid every month with no end date.

This replaces the earlier WebFetch paraphrase (F10.1–F10.5) with exact text; confirms all five earlier
facts and adds one new one not previously captured: **the ProjectX API cannot be used on a Live Funded
Account at all** ("Live funded accounts are not allowed to trade through the ProjectX API"). Note the
"Not allowed on a private server" list as rendered by the text extraction includes "Receiving copies of
your own fills, positions, and P&L" — this item's column placement is ambiguous in the extracted plain
text (the page renders it as a two-column table; the raw text lost the column boundary for this row).
Given the surrounding sentence "your server can watch and record, but it cannot trade," and that
receiving fill/position/P&L copies is a "watch and record" activity, this item most likely belongs in
the "Allowed" column — flagged as a table-extraction ambiguity, not resolved from the plain-text
extraction; the lead should treat this one row as unconfirmed until checked against the rendered page.

### F12.3 — Q3: holiday trading hours and the early-close flatten rule

Source: `https://help.topstep.com/en/articles/13350348-topstep-holiday-trading-hours` ("Topstep Holiday
Trading Hours"), fetched verbatim via curl, page marked "Updated this week."

> Holidays bring shortened or closed markets. All account types must close positions 15 minutes before
> any early close. Positions still open at the cutoff are auto-liquidated. Topstep emails details before
> each holiday.
>
> Position Close Rule — Close all positions 15 minutes before early close (e.g., close by 11:45 CT for a
> 12:00 CT close). Applies to: Trading Combine®, Express Funded Account® (XFA), Live Funded Account®
> (LFA). Open positions at the cutoff will be auto-liquidated.

This **CONFIRMS** the Stage A.1 finding exactly: 15 minutes before any early close, across all account
types.

2026 Holiday Schedule (verbatim table):

| Holiday | Date | Close Positions By | Reopen After |
|---|---|---|---|
| New Year's Day | Thu Jan 1, 2026 | Markets closed | 17:00 CT (for 1/2 trade date) |
| MLK Day | Mon Jan 19, 2026 | 11:45 CT | 17:00 CT Mon Jan 19 |
| Presidents' Day | Mon Feb 16, 2026 | 11:45 CT | 17:00 CT Mon Feb 16 |
| Good Friday | Fri Apr 3, 2026 | 08:00 CT | 17:00 CT Sun Apr 5 |
| Memorial Day | Mon May 25, 2026 | 11:45 CT | 17:00 CT Mon May 25 |
| Juneteenth | Fri Jun 19, 2026 | SIM: 11:45 CT / Live: 11:10 CT | 17:00 CT Sun Jun 21 |
| Independence Day | Fri Jul 3, 2026 | 11:45 CT | 17:00 CT Sun Jul 5 |
| Labor Day | Mon Sep 7, 2026 | 11:45 CT | 17:00 CT Mon Sep 7 |
| Thanksgiving | Thu Nov 26, 2026 | 11:45 CT | 17:00 CT Thu Nov 26 |
| Day After Thanksgiving | Fri Nov 27, 2026 | 12:00 CT | 17:00 CT Sun Nov 29 |
| Christmas Eve | Thu Dec 24, 2026 | 12:00 CT | — |
| Christmas Day | Fri Dec 25, 2026 | Markets closed | 17:00 CT Sun Dec 27 |
| New Year's Day | Fri Jan 1, 2027 | Markets closed | 17:00 CT Sun Jan 3 |

CME Protocol / blended trade-date rule (verbatim):

> On certain holidays, the CME ... may blend multiple calendar days into a single trading day — meaning
> all profits, losses, and drawdowns accumulated across that window are counted together as one session.
> ... If you hit your DLL during the abbreviated holiday session (e.g., Monday), your account will be
> locked for the remainder of that blended trading day — which may extend into Tuesday's session.
>
> | Account Type | CME Protocol |
> |---|---|
> | Live Funded Account® | Yes |
> | Trading Combine® | No |
> | Express Funded Account® | No |

Note: this page's schedule does not list Independence Day for years 2019–2023 (it covers 2026–2027
only); the D.1f session's finding about a 12:00 CT Independence Day halt in 2019–2023 cannot be
cross-checked against this page and remains sourced to whatever calendar data D.1f used, not to this
Topstep help article.

### F12.4 — Q4: how QM, QG, M6E, M6A, M6B count against the lot limit

**Not published as an explicit, named rule.** Checked: 8284223 (Scaling Plan — its "Special Product
Weightings" table names only SIL, MBT, MET; QM, QG, M6E, M6A, M6B are absent from that table), 8284197
(Trading Combine Parameters — Max Position Size table gives only "Max Contracts" / "Max Micros" columns
with no per-product multiplier), 8284113 ("Can I trade Forex with You?" — lists 6A/6B/6C/6E/E7/6J/6S/6N
and the micros M6E/M6A/M6B as available FX Futures products and repeats the same generic Max Contracts
table by account size, with no per-product ratio), and 13613539 (Risk Adjustments — QM appears only
inside the volatility-restriction table, e.g. "E-Mini Crude Oil (QM) = 3/6/9," a conditional cap, not a
standing lot-counting rule; QG, M6E, M6A, M6B do not appear anywhere in that page).

Plain statement: Topstep's only published lot-counting rule is the generic one on 8284223 — "Micros and
minis count at a 10:1 ratio... 1 Mini = 10 Micro contracts" — plus the three named exceptions (SIL,
MBT, MET). Since QM (E-Mini Crude Oil) and QG (E-Mini Natural Gas) are not listed as "Micro" products
anywhere and are not named in the Special Product Weightings exception table, the page's own
categorization implies they count as standard 1-lot "mini" contracts identical to CL/NG for position-
limit purposes — but no page states this explicitly for QM/QG by name. Likewise M6E, M6A, and M6B are
prefixed "Micro" and not listed as exceptions, implying the standard 10:1 micro count against their
non-micro counterparts (6E, 6A, 6B respectively) — but again, no page names M6E/M6A/M6B specifically in
a weighting table the way SIL/MBT/MET are named. **Verdict: inferred from the general rule and the
absence of these five symbols from every exception list found, but not directly quotable as an explicit
per-symbol statement.**

## Differences From Planning Chat — Summary List

1. F1: MBT, MET, SIL, MES, MNQ, M2K, MYM, M6E, M6A, MCL, MGC, 6M are now starred on the permitted-products page; the planning chat's list had these unstarred (with MBT/MET/SIL called out separately for scaling, not starring). MNG appears on the current page but was not in the planning chat's enumerated list. MBT/MET sit inside "CME Equity Futures," not a separate "CME crypto" group. **DIFFERS.**
2. F4 daily close (15:10 CT) and flatten start (15:08 CT): **CONFIRMS** exactly.
3. F5 position limit for 50K ("5 minis or 50 micros"): **CONFIRMS** exactly (5 max contracts, 50 max micros).
4. F6 news-trading restriction: planning chat's premise of restricted events/time windows does not match; Topstep affirmatively allows news trading in both SIM and Funded Accounts, prohibiting only full-Max-Position-Size entries into a scheduled major news event. **DIFFERS** (in the sense that no blackout-window rule exists).
5. F8 limit-order fill rule ("market must trade through the price"): **CONFIRMS** exactly.
6. F7 page dates: 10305426 confirmed "June 10, 2026" as stated in the planning chat. F1 page confirmed "July 13, 2026" as stated in the planning chat.
