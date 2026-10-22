# Stage E.28 A2: Layer 2 firm facts, Topstep (as of 2026-10-21)

Worker: A2_topstep (Opus 5.5, xhigh brief). Started 2026-10-21 ~05:40 PDT. Facts only; no scoring (ranking spec
section 3 is the lead's). Raw pages, their UTC/PDT fetch times and sha256 are in
`reports/stage_e28_briefs/pages/A2_topstep/log.tsv`; text extractions are `<file>.txt` next to each raw file
(first line `DATEMODIFIED:` is the help article's JSON-LD dateModified, UTC). All quotes below are verbatim from
those `.txt` files (whitespace collapsed; table cells appear as separate lines in the .txt). Machine-readable twin:
`A2_firm_topstep.json`.

Fetch method and terms decision: every page was fetched by curl (one request each, 3.5 s apart, browser headers),
all HTTP 200 except `www.topstep.com/pricing` (404: no such page). Before the first curl, the E.19 copy of the
Terms of Use (Last updated September 21, 2026) was read: section 28 bans "Using any manual or automated software,
devices, or other processes to “crawl” or “spider” any web pages contained in the Sites or Services;" and has no
general ban on automated access; robots.txt allows the article and www paths (help centre Crawl-delay 1). Decision:
targeted single-page retrieval, no link-following, no Scrapling. Today's Terms (ts_terms_of_use.html.txt L13) still
read "Last updated: September 21, 2026" with the same clause (L232); today's robots.txt files are byte-identical to
E.19's (sha256 8db9cabbe212..., 47f8552e0c17...). No Scrapling, Firecrawl or deviation fetch was used on topstep.com.

## 1. The standard 50K plan and its funded stage

### 1.1 Which plan is "the standard 50K plan"

The www pricing card (`ts_www_topstep-prop.html.txt`, L55-69) lists, in order: "Standard", "No Activation Fee",
"Responsible Trading Advantage" (a toggle "On / Off"), then "$50K Buying Power" "$49" "$85" "/month". The help
centre pricing article (`ts_14289835.html.txt`, dateModified 2026-10-15T22:44:35Z) gives the table
"Account Size | Standard Path | No Activation Fee Path" with "50K | $49/month | $95/month". So the first 50K plan
on the pricing page is the **50K Trading Combine, Standard Path, $49/month**. (Interpretation, not a quote: the
www "$85" is the No Activation Fee price $95 less the "$10 off → 50K" Responsible Trading Discount; the static
HTML does not label it. The lead decides the plan; the facts for both paths are below.)

### 1.2 Trading Combine (evaluation), 50K

| Item | Value | Source file | Verbatim quote |
|---|---|---|---|
| Price, Standard Path | USD 49 per month, recurring | ts_14289835.html.txt | "50K" / "$49/month" (Standard Path column); "Standard Path: Lower monthly cost. $149 Activation Fee charged once per Express Funded Account (XFA) earned." |
| Price, No Activation Fee Path | USD 95 per month | ts_14289835.html.txt | "No Activation Fee Path" ... "$95/month"; "No Activation Fee Path: Higher monthly cost. No fee when you pass." |
| Discount with DLL at purchase (NAF path only) | USD 10 off per month at 50K | ts_14289835.html.txt | "There's now a Responsible Trading Discount when you add a DLL at purchase for No Activation Fee Trading Combines" ... "$10 off → 50K" ... "Discount recurs monthly." |
| Billing | monthly subscription, rebills every 30 days, no time limit | ts_8284121.html.txt (dateModified 2026-10-12) | "The Trading Combine® is a monthly subscription. It Rebills every 30 days from your original sign-up date. Active until you pass and earn an Express Funded Account® (XFA) — or until you cancel. No time limit for passing." |
| Path is fixed | cannot change after purchase | ts_14289835.html.txt | "⚠️ Important: Paths cannot be changed after purchase." |
| Profit target | USD 3,000 | ts_8284208.html.txt (2026-09-17); ts_www_topstep-prop.html.txt L74 | "$50K" / "$3,000" / "Less than $1,650" (Profit Target, Best Day Recommendation); www: "Profit Target:" "$3,000" |
| Maximum Loss Limit (MLL) | USD 2,000, trailing on end-of-day balance, monitored intraday on unrealized P&L, locks at starting balance | ts_8284204.html.txt (2026-09-18) | "$50K" / "$2,000"; "The MLL is a trailing limit. It rises as your end-of-day balance grows, but never moves down. Once it reaches your starting balance, it locks permanently."; "The MLL updates at the end of each trading day but is monitored in real time throughout the session. Both realized and unrealized P&L count toward it." |
| MLL example | start 50,000, MLL 48,000 | ts_8284204.html.txt | "You start a 50K Trading Combine. Balance: $50,000. MLL: $48,000." |
| Breach consequence (Combine) | liquidated, ineligible until Reset; subscription keeps rebilling | ts_8284204.html.txt; ts_8284121.html.txt | "Trading Combine: Your account is liquidated for the rest of the trading day and becomes ineligible for funding until you Reset."; "The subscription does not cancel — it keeps rebilling, and you can still trade for practice. You'll get a Reset Credit when your Rebill processes." |
| Daily Loss Limit (DLL) | optional; USD 1,000 at 50K if added at checkout (fixed, carries into XFA); hitting it is not a violation | ts_10490293.html.txt (2026-06-30) | "The Daily Loss Limit (DLL) is optional in the Trading Combine® and Express Funded Account® (XFA)."; "$50K Account: $1,000"; "Daily Loss Limit at checkout is fixed (no changes later)"; "Applies to your Express Funded Account after you pass"; "Triggering it is not a rule violation — it's a forced break for the rest of that session." |
| Consistency rule | best single day must be at most 55% of profit target, else target rises to best day / 0.55 | ts_8284208.html.txt | "Your single best day of profit must stay at or below 55% of your Profit Target. If it exceeds that, your Profit Target increases."; "To find your new Profit Target: Best Day ÷ 0.55 = Total Profit Needed."; "55% is a hard line. It is not rounded, and there is no buffer." |
| Minimum days | 2 (implied by the 55% rule) | ts_8284197.html.txt (2026-09-24) | "You can pass in as few as two days, but keep your best day below 55% of your Profit Target." |
| Time limit | none | ts_8284121.html.txt | "No time limit for passing." |
| Max position size | 5 minis or 50 micros (10:1) | ts_8284197.html.txt | "Micros and minis count at a 10:1 ratio." / "$50K" / "5" / "50" |
| Reset fee | USD 49 (Standard), USD 95 (NAF) at 50K; one Reset Credit per rebill; max 2 resets per account per day; reset pushes the rebill date 30 days | ts_14289835.html.txt; ts_8284128.html.txt; ts_10370307.html.txt | Reset Pricing "50K" / "$49" / "$95"; "Every monthly Rebill adds 1 Reset Credit to your Reset Bank."; "Resetting your account pushes your Rebill date out 30 days from the date of purchase."; "2 Resets per account per calendar day" |
| Reset credit expiry | 1 year for credits issued on or after 2025-12-11 | ts_8284128.html.txt | "Credits issued on or after 12/11/2025 — expire 1 year after added" |
| Number of Combines | unlimited | ts_10370307.html.txt; ts_8284197.html.txt | "No limit on Trading Combine purchases"; "There's no limit to the number of Trading Combines you can have." |
| Simulated round-turn fee in the Combine | stated two ways (conflict) | ts_8284229.html.txt (2026-10-19); ts_8284213.html.txt (2026-09-30) | LFA costs page: "In the Trading Combine®, a $3.70/lot simulated fee is charged to emulate these real-world costs." The commissions page says its per-product fees "apply when trading the Trading Combine, Express Funded Account, and Live Funded Account." See section 2. |
| Trading day | 5:00 PM CT to 3:10 PM CT next day | ts_8284197.html.txt | "The trading day runs from 5:00 PM CT through 3:10 PM CT the next calendar day." |
| After passing | Combine closes, subscription cancels; profits do not carry over | ts_8284197.html.txt | "When a 50K, 100K, or 150K Trading Combine® ... passes, the account closes and the subscription is canceled."; "Profits don't transfer. Money made in the Trading Combine does not carry over to your Express Funded Account." |

### 1.3 Express Funded Account (XFA), the funded stage: simulated

| Item | Value | Source file | Verbatim quote |
|---|---|---|---|
| Sim or live | simulated; real-money payouts on sim results | ts_8284215.html.txt (2026-08-05) | "The Express Funded Account® (XFA) is the simulated funded-level account you earn after passing your Trading Combine."; "Topstep pays you real money based on your simulated trading results." |
| Activation fee | USD 149 one-time (Standard Path); USD 0 (NAF path) | ts_8284217.html.txt (2026-09-24) | "Standard Path" / "$149 one-time activation fee per XFA" / "No Activation Fee Path" / "No activation fee" |
| Monthly fee after passing | none | ts_8284215.html.txt | "No monthly subscription fee after passing." |
| Starting balance | USD 0 (50K is buying power) | ts_8284215.html.txt | "Your balance starts at $0 and grows from your trading profits." |
| MLL | starts at -2,000, trails up on end-of-day balance, locks at 0 when balance reaches 2,000; set to 0 after first payout | ts_8284204.html.txt | "For a 50K XFA, your MLL starts at -$2,000 and trails upward. Once your balance reaches $2,000, the MLL locks at $0 permanently."; "After your first Payout: Your MLL is set to $0 regardless of where it was before." |
| MLL breach | account closed (end of day); Back2Funded possible | ts_8284204.html.txt; ts_8284215.html.txt | "Express Funded Account: Your account is permanently closed. Back2Funded may be available if you're eligible."; "Your account is liquidated and closed at the end of the day." |
| DLL | optional (USD 1,000 at 50K, if added) | ts_8284215.html.txt | "Daily Loss Limit (DLL)" / "Optional" / "Optional" |
| Payout paths | Standard (5 winning days of USD 150+) or Consistency (3 traded days, best day at most 40% of net profit); chosen at activation, fixed | ts_8284215.html.txt; ts_8284233.html.txt | "5 winning days of $150+" / "3 days traded, 40% consistency target"; "Once you select XFA Consistency or Standard, that choice cannot be changed either." |
| Standard path detail | 5 winning days of USD 150+ net, not consecutive; positive net profit since last payout (not for the first); day locks 4:00 PM CT | ts_8284233.html.txt (2026-10-13) | "5 winning days of $150+ Net P&L. Days don't need to be consecutive. A day locks in at 4:00 PM CT. The trading day your Payout is requested doesn't count toward your next 5."; "You must have earned at least $0.01 since your last Payout. Your first Payout is exempt." |
| Consistency path detail | 3 days with at least 1 trade; largest day / total net profit at most 40% | ts_8284233.html.txt | "3 trading days with at least 1 trade per day."; "Your largest single day cannot exceed 40% of your total net profit." |
| Payout size | 50% of balance per request, capped | ts_8284233.html.txt | "Max Payout per request: 50% of your account balance up to the cap below." |
| Payout caps, 50K | Standard USD 2,000; Consistency USD 3,000 | ts_8284233.html.txt | "$50K" / "$2,000" / "$3,000" |
| Double caps with DLL added at Combine purchase (promotion) | Standard USD 4,000; Consistency USD 6,000 at 50K; from 2026-06-02, no end date set | ts_8284233.html.txt; ts_www_double-payout-caps-terms-conditions.html.txt | "$50K" / "Standard" / "$2,000" / "$4,000" / "$50K" / "Consistency" / "$3,000" / "$6,000"; "Only if you already added the DLL when you purchased your Trading Combine."; "This offer begins on June 2, 2026. No end date has been established at this time." |
| Profit split | 90/10 | ts_8284233.html.txt | "90/10 profit split — you keep 90%" |
| Legacy split note | 100% of first USD 10,000 for traders who joined the new dashboard before 2026-01-12 | ts_8284233.html.txt | "Note for traders who joined the new Topstep dashboard before January 12, 2026: You receive 100% of your first $10,000 in lifetime profits." |
| Minimum payout | USD 125 | ts_8284233.html.txt | "Minimum Payout: $125" |
| Frequency | no calendar frequency; each request needs a fresh 5 winning days (Standard) or 3 days (Consistency) | ts_8284233.html.txt | "After each Payout: Your Maximum Loss Limit (MLL) resets to $0 permanently, and your 5-day count restarts." |
| Payout fees | ACH USD 30, Wire/SWIFT USD 30; Wise and Aeropay no Topstep fee | ts_8284233.html.txt | "ACH" / "US banks only" / "1-3 business days" / "$30"; "Wire/SWIFT" / "International" / "5-10 business days" / "$30"; "Wise" / "China, Canada, UK" / "1-3 business days" / "No Topstep fee**" |
| Approval time | internal approval 1-3 business days | ts_8284233.html.txt | "Internal approval can take 1-3 business days." |
| Scaling plan, 50K XFA | balance < 1,500: 2 lots; 1,500-2,000: 3 lots; > 2,000: 5 lots (mini-equivalents, 10:1 micros) | ts_scaling_xfa_charts.png (image, sha256 55ec76b4b293..., byte-identical to E.19's copy); ts_8284223.html.txt (2026-07-16) | Image text (read visually): "$50K ACCOUNT" "Below $1,500 | 2 Lots" "$1,500 - $2,000 | 3 Lots" "Above $2,000 | 5 Lots". Page: "Your max contracts do not increase mid-session."; "1 Mini = 10 Micro contracts" |
| Scaling exceptions | SIL 5:1 vs SI and counts as 2 micros; MBT and MET capped at mini-equivalent lots | ts_8284223.html.txt | "Micro Silver (SIL)" / "5:1 ratio vs. Silver (SI); counts as 2 of any other micro"; "Micro Bitcoin (MBT)" / "Capped at mini-equivalent lot sizes, not standard micro scaling" |
| Scaling breach grace | under 10 s ignored | ts_8284223.html.txt | "Errors corrected in under 10 seconds are ignored." |
| Max accounts | 5 active XFAs; copier up to USD 750K buying power | ts_8284215.html.txt | "You can hold up to 5 active XFAs at a time."; "Yes, up to $750K buying power using a trade copier." |
| Inactivity | XFA may be closed after 30 days with no trades | ts_8284215.html.txt | "XFAs with no trading activity for more than 30 days may be closed." |
| Back2Funded | up to 2 reactivations before first payout; USD 599 at 50K (USD 50 off with DLL); 30-day window (was 7 until 2026-05-29) | ts_12060405.html.txt (2026-09-29); ts_14289835.html.txt | "Back2Funded gives you up to 2 Reactivations per account if you lose your Express Funded Account® (XFA) before your first Payout."; "$50K XFA" / "$599"; "On May 29th, 2026, the Reactivation window increased from 7 days to 30 days!" |
| Closing an XFA voluntarily | up to 50% of balance capped at USD 5,000, rest forfeited (www rules, dated 2025-06-26, stale page) | ts_www_express-funded-account-rules.html.txt L61 | "If you choose to close your Express Funded Account and are eligible for a payout, you may receive up to 50% of your current Reward Balance, capped at $5,000. Any remaining balance will be forfeited." |

### 1.4 Live Funded Account (LFA): discretionary call-up, live capital

| Item | Value | Source file | Verbatim quote |
|---|---|---|---|
| Call-up | discretionary Risk Team review; all XFAs close | ts_13747178.html.txt (2026-09-29); ts_10657969.html.txt (2026-10-20) | "All Traders are unique and the Risk Team reviews each Trader on a case by case basis"; "When the call-up comes, all Express Funded Accounts (XFA) close." |
| Call-up rate (2025) | 0.71% of XFA participants | ts_www_about-us.html.txt L140 | "(d) 0.71% of individual participants trading in an Express Funded Account were called up to a Live Funded Account." |
| Starting balance | 20% of capped cumulative XFA balance tradable (min 10,000), 80% reserve released 25% per profit target (3,000 at 50K) | ts_10657969.html.txt | "20% available to trade immediately — minimum $10,000"; "80% held in Reserve — released in 4 increments of 25% as you hit profit thresholds"; "$50K" / "$3,000" |
| LFA DLL | USD 2,000 at 50K; 2,000/5 contracts if tradable balance <= 10,000; 1,000/3 if <= 5,000 | ts_10657969.html.txt | "$50K" / "$2,000"; "$10,000 or below" / "$2,000" / "5"; "$5,000 or below" / "$1,000" / "3" |
| LFA payouts | 5 winning days of 150+ per cycle, 50% of balance, no cap; daily after 30 winning days | ts_8284233.html.txt | "Request up to 50% of your account balance with no dollar cap"; "Once you've earned $150+ Net P&L on 30 non-consecutive days in your Live Funded Account, you unlock daily Payouts" |
| LFA costs | CME professional data USD 133 per exchange per month (1 covered); commissions deducted live; own platform licence | ts_8284229.html.txt | "Data fee: $133 per exchange, per month"; "Topstep covers 1 exchange for all LFA Traders." |
| LFA and API | ProjectX API not allowed on Live | ts_11187768.html.txt | "No, Live funded accounts are not allowed to trade through the ProjectX API. The API Gateway is built for the simulated environment and isn't available on Live." |
| Low-balance closure | LFA balance below 1,000 may be liquidated and closed | ts_10657969.html.txt | "If your LFA balance drops below $1,000, the account may be immediately liquidated and closed at end of the trading day." |

### 1.5 Simulator mapping notes (for EconCoder; facts, not decisions)

- Combine: start 50,000; MLL = max(trailing EOD high-water balance - 2,000) capped at 50,000, checked intraday on
  net (realized + unrealized) P&L; pass when cumulative profit >= max(3,000, best_day / 0.55) and at least 2 days;
  monthly fee 49 (Standard) every 30 days while not passed; on breach either buy a reset (49, pushes rebill 30 days)
  or wait for the next rebill's free reset credit; at most 2 resets per day; no time limit.
- XFA: start 0; MLL -2,000 trailing on EOD balance, locks at 0 once balance >= 2,000, and is set to 0 at the first
  payout; activation 149 (Standard path); payout per request = min(50% of balance, 2,000) (Standard path) with 90%
  to the trader, minus 30 if ACH/wire (Wise 0 for Canada); needs 5 non-consecutive days of net >= 150 since the last
  request and positive net since the last payout (not for the first). Scaling plan 2/3/5 mini-equivalents.
  Back2Funded 599 up to 2 times, only before the first payout, within 30 days.
- Optional DLL 1,000 (fixed if chosen at purchase) gives double caps (4,000 Standard) at 50K under the June 2026
  promotion, and on the NAF path a 10/month discount.
- The LFA call-up is discretionary (0.71% of XFA participants in 2025) and the API is not available on Live; a
  conservative mapping treats the XFA as the terminal stage.

## 2. Products, commissions and fees, position limits (50K)

Sources: `ts_8284206.html.txt` (When and What Products Can I Trade?, dateModified 2026-07-13T21:22:30Z) for the
permitted list; `ts_8284213.html.txt` (TopstepX Commissions and Fees, dateModified 2026-09-30T21:00:42Z) for the
round-turn (RT) costs. The fee page says: "These fees apply when trading the Trading Combine, Express Funded
Account, and Live Funded Account." and "Round-Turn (RT) cost: charged when you complete both sides of a trade.
Each side (Buy or Sell) incurs half the total, also called a "per side" fee." Breakdown: "$0.02 round turn ($0.01
per side)" NFA fee; "Minis $1.00 round turn ($0.50 per side)"; "Micros $.50 round turn ($0.25 per side)"; the
exchange fee is the rest ("Exchange fees are set by the exchange and do not include the regulatory fee."). Per
side = RT / 2 (the page's own rule). The table cell quote is the product label followed by its RT total, e.g.
"Micro Crude Oil (MCL)" / "$1.72". The MCL and MNG totals already include the CME increase from the 2026-10-01
trading day ("MCL: $0.50 to $0.60 per side ($1.20 round turn)", "MNG: $0.60 to $0.70 per side ($1.40 round turn)").

| Code | Listed (permitted) | RT USD | Per side USD | Commission RT (class) | Note |
|---|---|---|---|---|---|
| MNG | yes "Micro Henry Hub Natural Gas (MNG)" | 1.92 | 0.96 | 0.50 (micro) | exch 1.40 RT from 2026-10-01 |
| QG | yes "E-mini Natural Gas (QG)" | 2.02 | 1.01 | 1.00 (mini) | |
| NG | yes "Natural Gas (NG)" | 4.22 | 2.11 | 1.00 | |
| MCL | yes "Micro Crude Oil (MCL)*" | 1.72 | 0.86 | 0.50 | exch 1.20 RT from 2026-10-01; volatility cap 30 micros at 50K |
| QM | yes "E-mini Crude Oil (QM)" | 3.42 | 1.71 | 1.00 | volatility cap 3 at 50K |
| CL | yes "Crude Oil (CL)" | 4.02 | 2.01 | 1.00 | volatility cap 3 at 50K |
| MGC | yes "Micro Gold (MGC)*" | 1.92 | 0.96 | 0.50 | volatility cap 30 at 50K; Tier 1 news cap |
| GC | yes "Gold (GC)" | 4.32 | 2.16 | 1.00 | volatility cap 3; Tier 1 news: no new opens |
| SIL | yes "Micro Silver (SIL)*" | 2.72 | 1.36 | 0.50 | counts as 2 micros; volatility cap 2 at 50K |
| SI | listed, **currently 0 contracts** "Silver (SI) = 0" | 4.32 | 2.16 | 1.00 | volatility restriction, ts_13613539 |
| MHG | yes "Micro Copper (MHG)" | 1.92 | 0.96 | 0.50 | volatility cap 2 at 50K |
| HG | listed, **currently 0 contracts** "Copper (HG) = 0" | 4.32 | 2.16 | 1.00 | volatility restriction |
| M6E | yes "Micro Euro FX (M6E)*" | 1.00 | 0.50 | 0.50 | fee table label "Micro EUR/USD (M6E)" |
| 6E | yes "Euro FX (6E)" | 4.22 | 2.11 | 1.00 | |
| M6A | yes "Micro AUD/USD (M6A)*" | 1.00 | 0.50 | 0.50 | |
| 6A | yes "Australian $ (6A)" | 4.22 | 2.11 | 1.00 | |
| MET | yes "Micro Ether (MET)*" | 0.72 | 0.36 | 0.50 (inferred micro) | scaling: "Capped at mini-equivalent lot sizes" |
| ETH (CME Ether) | **not listed** | - | - | - | absent from permitted list and fee table |
| MBT | yes "Micro Bitcoin (MBT)*" | 2.82 | 1.41 | 0.50 (inferred micro) | scaling: capped at mini-equivalent lots |
| BTC | **not listed** | - | - | - | |
| M2K | yes "Micro E-mini Russell 2000 (M2K)*" | 1.22 | 0.61 | 0.50 | Tier 1 news cap 3 at 50K |
| RTY | yes "E-mini Russell 2000 (RTY)" | 3.78 | 1.89 | 1.00 | Tier 1 news: no new opens |
| MYM | yes "Micro Mini-DOW (MYM)*" | 1.22 | 0.61 | 0.50 | Tier 1 cap |
| YM | yes "Mini-DOW (YM)" | 3.78 | 1.89 | 1.00 | Tier 1 block |
| MNQ | yes "Micro E-mini NASDAQ 100 (MNQ)*" | 1.22 | 0.61 | 0.50 | Tier 1 cap |
| NQ | yes "E-mini NASDAQ 100 (NQ)" | 3.78 | 1.89 | 1.00 | Tier 1 block |
| 2YY, 5YY, 10Y, 30Y | **not listed** | - | - | - | micro Treasury yield futures absent |
| ZT | yes "2-Year Note (ZT)" | 2.32 | 1.16 | 1.00 | |
| ZF | yes "5-Year Note (ZF)" | 2.32 | 1.16 | 1.00 | |
| ZN | yes "10-Year Note (ZN)" | 2.62 | 1.31 | 1.00 | |
| ZB | yes "30-Year Bond (ZB)" | 2.76 | 1.38 | 1.00 | |
| Micro grains (MZC, MZS, MZW, MZL, MZM) | **not listed** | - | - | - | |
| XC, XK, XW (mini grains) | **not listed** | - | - | - | |
| ZC | yes "Corn (ZC)" | 5.28 | 2.64 | 1.00 | special hours (section 3) |
| ZS | yes "Soybeans (ZS)" | 5.28 | 2.64 | 1.00 | fee label "Soybean (ZS)" |
| ZW | yes "Wheat (ZW)" | 5.28 | 2.64 | 1.00 | |
| ZL | yes "Soybean Oil (ZL)" | 5.28 | 2.64 | 1.00 | |
| ZM | yes "Soybean Meal (ZM)" | 5.28 | 2.64 | 1.00 | |

Other listed products not in the candidate set: ES 3.78, MES 1.22, NKD 5.32, PL 4.32 (currently 0), RB 4.02,
HO 4.02, 6B/6C/6J/6S/6M/6N 4.22, E7 2.72, M6B 1.00, UB 2.92, TN 2.62, HE 5.22, LE 5.22.

Asterisks: the product page says "See Prohibited Conduct for restrictions on specific products marked with an
asterisk (*)." Today's Prohibited Conduct article (`ts_10296582.html.txt`, dateModified 2026-09-30) names no
product. Unresolved: the asterisk's meaning is not documented on the pages read (most plausibly the micro caps
in the Tier 1 and volatility tables, but that is an inference).

**Conflict on the Combine's simulated fee.** `ts_8284229.html.txt` (LFA costs, dateModified 2026-10-19): "In the
Trading Combine®, a $3.70/lot simulated fee is charged to emulate these real-world costs." The commissions page
says its per-product table applies to the Trading Combine too. The same LFA page gives example round turns that
differ from the commissions table ("Crude Oil (CL): $1.54", "Gold (GC): $4.24", "E-mini S&P 500 (ES): $3.80" against
4.02, 4.32 and 3.78). The commissions page is the product-specific one; the lead decides.

### Position limits at 50K

| Stage | Limit | Source | Quote |
|---|---|---|---|
| Combine | 5 minis or 50 micros, 10:1 | ts_8284197.html.txt | "Micros and minis count at a 10:1 ratio." "$50K" / "5" / "50" |
| XFA | scaling 2 / 3 / 5 mini-equivalents by balance (<1,500 / 1,500-2,000 / >2,000) | ts_scaling_xfa_charts.png | see 1.3 |
| Product exceptions | SIL 5:1 vs SI, counts as 2 micros; MBT and MET capped at mini-equivalent lots | ts_8284223.html.txt | "Micro Silver (SIL)" / "5:1 ratio vs. Silver (SI); counts as 2 of any other micro" |
| Current volatility restrictions (Combine, XFA, Pro; format 50K/100K/150K) | CL, QM, RB, HO = 3; MCL = 30; GC = 3; MGC = 30; SI = 0; SIL = 2; HG = 0; MHG = 2; PL = 0 | ts_13613539.html.txt (2026-10-20T19:42:21Z, identical sha256 to E.26's copy 085db4d216de) | "Crude Oil (CL) = 3/6/9", "Micro Crude Oil (MCL) = 30/60/90", "Gold (GC) = 3/6/9", "Micro Gold (MGC) = 30/60/90", "Silver (SI) = 0", "Micro Silver (SIL) = 2/5/7", "Copper (HG) = 0", "Micro Copper (MHG) = 2/5/7" |
| XFA ceiling for restricted products | the lower of the volatility cap and the scaling plan; 50K XFA restricted energies/gold: "Below $1500 balance = 1 mini / 12 micros", "$2,000 balance = 3 mini / 31 micros"; SIL/MHG "$2,000 balance = 2 micros" | ts_13613539.html.txt | "For Express Funded Accounts, position limits for restricted products have a ceiling of the contracts listed above (CL = 3/6/9, for example)." |
| LFA | micro-to-mini ratio not available in LFA; LFA column of the volatility table differs (MCL 3/6/9, MGC 5/10/15, SIL/MHG 2/4/6) | ts_8284197.html.txt; ts_13613539.html.txt | "It is not currently available for the Live Funded Account." |

## 3. Product restrictions: news, hours, flat-by times

| Item | Value | Source | Quote |
|---|---|---|---|
| Tier 1 news window | 5 min before to 5 min after CPI, FOMC rate decision, FOMC press conference, NFP, PPI (CT 07:25-07:35; 12:55-13:05; 13:25-13:35) | ts_13613539.html.txt | "Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after)." Table rows "Consumer Price Index (CPI)" "7:30 AM" "7:25 to 7:35 AM" ... "Producer Price Index (PPI)" "7:30 AM" "7:25 to 7:35 AM" |
| Tier 1 micro caps at 50K | MES, M2K, MYM, MNQ, MGC: 3 opening contracts (Combine); MHG and SIL: 2; 50K XFA 0/1 below 2,000 balance, 0/3 above | ts_13613539.html.txt | "Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes"; "MHG and SIL: Opening transactions limited to 1, 2, 5, 7, 12 contracts" |
| Products unaffected by Tier 1 | energies, rates, FX | ts_13613539.html.txt | "Other products (energies, rates, FX, etc.) are unaffected." |
| Pending orders in the window | do not fill; new pending orders for the window cannot be placed; closing brackets accepted | ts_13613539.html.txt | "Pending orders are not open positions. They will not fill during the 10-minute window, and new pending orders intended to execute during this timeframe cannot be placed. TP/SL brackets that are reducing/closing positions will be accepted during the window." |
| Existing positions | may be held through the window | ts_13613539.html.txt | "Traders holding existing positions in equity index products and metals prior to 5 minutes before the news event may keep them open and manage them through the Tier 1 News Events window." |
| Prohibited strategy tied to news | full max size into scheduled major news | ts_10305426.html.txt | "Purposefully trading your full Maximum Position Size directly into a scheduled major news event." |
| EIA reports | listed as common releases; no restriction stated | ts_8284211.html.txt (2026-10-15) | "Crude Oil Inventories (EIA)" "9:30 AM / 10:00 AM"; "Natural Gas Inventories (EIA)" "9:30 AM" |
| Flat-by time | 3:10 PM CT every weekday; auto-cancel begins 3:10; risk managers begin flattening 3:08; product's own earlier close applies | ts_8284206.html.txt | "All positions must be closed by 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT. No swing trading."; "Avoid opening new positions after 3:08 PM CT — Risk Managers begin flattening at that time."; "If you're trading a product with an earlier daily close than 3:10 PM CT, you must exit before that product's close." |
| Session | Sunday 5:00 PM CT open; weekdays 5:00 PM to 3:10 PM CT; Friday close 3:10 PM | ts_8284206.html.txt | "Sunday open" "5:00 PM CT" "Weekday close" "3:10 PM CT" "Weekday reopen" "5:00 PM CT" "Friday close" "3:10 PM CT (closed till Sunday at 5:00 PM)" |
| CBOT grains hours | 7:00 PM-7:45 AM and 8:30 AM-1:20 PM CT; no orders 7:45-8:30 | ts_8284206.html.txt | "CBOT Commodity Products (Corn, Wheat, Soybeans, Soybean Meal, Soybean Oil):" "Sunday–Monday: 7:00 PM – 7:45 AM CT" "Monday–Friday: 8:30 AM – 1:20 PM CT"; "CBOT Commodity Market Pause (Mon–Fri): 7:45 AM – 8:30 AM CT. No orders accepted during this window." |
| Holidays | flat 15 minutes before any early close | ts_13350348.html.txt (2026-09-18) | "All account types must close positions 15 minutes before any early close. Positions still open at the cutoff are auto-liquidated." |
| Price-limit rule | no position within 2% of a CME price limit | ts_10296582.html.txt; ts_8284225.html.txt | "Holding a position within 2% of a product’s price lock limit" |
| Volatility restrictions | temporary product caps (section 2), currently on energies and metals | ts_13613539.html.txt | "During extreme volatility, we may temporarily tighten position limits on affected products." |

Hours note: the CME Globex hours themselves were not fetched here (cmegroup.com is blocked from this machine);
the Topstep session (17:00 to 15:10 CT) cuts the last 50 minutes of a 17:00-16:00 CT Globex day for products
that trade to 16:00 CT [Globex hours unverified in this file].

## 4. Automation, API and trading-style rules

| Item | Value | Source | Quote |
|---|---|---|---|
| Automated strategies, Combine | allowed "with conditions" | ts_8284197.html.txt | "Can I use automated trading strategies?" "Yes, with conditions. Topstep won't help set up or troubleshoot automated strategies, and no exceptions are made for errant trades or malfunctions." |
| Automated strategies, XFA | allowed "with conditions" | ts_8284215.html.txt | "Can I use automated strategies?" "Yes, with conditions. Topstep won't help set them up or cover malfunctions." |
| Custom bots via API | allowed, subject to an HFT prohibition | ts_11187768.html.txt (2026-09-17) | "Yes. Custom automated strategies and bots are allowed via the TopstepX / ProjectX API, subject to standard platform rules and our prohibition on highfrequency trading (HFT)." |
| API on Live (LFA) | not allowed | ts_11187768.html.txt | "No, Live funded accounts are not allowed to trade through the ProjectX API." |
| Which API | TopstepX / ProjectX Gateway API (REST + WebSocket), USD 29/month, USD 14.50 with code | ts_11187768.html.txt | "It's powered by ProjectX and billed separately from your Topstep subscription."; "API Access is $29/month. Topstep Traders get 50% off with code topstep — that's $14.50/month, valid every month with no end date." |
| Other APIs (Tradovate, Rithmic, NinjaTrader) | none offered today; Oct 2025 page still named NinjaTrader, Quantower, Tradovate, TradingView | ts_14434175.html.txt; wb2025_ts_8284197.html.txt L71 | No mention of Tradovate, Rithmic or NinjaTrader on any of today's 43 help pages (grep). 2025-09-18 Wayback: "All other trading platforms, including, but not limited to, NinjaTrader, Quantower, Tradovate, and TradingView still have the Daily Loss Limit O[n]..." |
| API rate limit | 200 requests per 60 s (all endpoints except bar history); 50 per 30 s for bars; HTTP 429 | px_rate_limits.html.txt (gateway.docs.projectx.com, fetched today) | "All other Endpoints | 200 requests / 60 seconds"; "POST /api/History/retrieveBars | 50 requests / 30 seconds" |
| Native brackets on API | stopLossBracket / takeProfitBracket on order place, in "Auto OCO Brackets" mode | px_order_place.html.txt | "Auto OCO Brackets. Brackets attach to each order. stopLossBracket and takeProfitBracket are accepted on this endpoint." |
| Order types (platform) | Market, Limit, Stop, Trailing Stop, OCO, OSO | ts_8765442.html.txt | "All order types below are available on TopstepX™." |
| VPS / remote servers | prohibited for order transmission; allowed for research, logging, read-only | ts_11187768.html.txt; ts_terms_of_use.html.txt L233 | "All trading activity must originate from your personal device. The use of VPS, VPNs, and remote servers is prohibited by Topstep's Terms of Use."; "The line is order transmission: your server can watch and record, but it cannot trade."; Terms: "Using any VPN or VPS on Accounts is strictly prohibited and may result in account termination and forfeiture of profits." |
| HFT / short-term (Terms) | Terms give "short term or high frequency trades" as an example of prohibited manipulation | ts_terms_of_use.html.txt L212 | "...the purpose of which is to manipulate, abuse, or give User an unfair advantage while using the Site or Services, for example, by engaging in any short term or high frequency trades or simultaneously entering into opposite positions;" |
| Unfair technology | prohibited | ts_10305426.html.txt; ts_10296582.html.txt | "Using software, AI, ultra-high speed systems, or mass data entry that manipulates, abuses, or provides an unfair advantage on the platform or in the program." |
| Minimum hold / order-rate rule | none published as a number; SIM-exploit examples describe "hundreds or thousands of trades per day, with average durations measured in seconds, not minutes" | ts_10305426.html.txt | "The behaviors above are intentional and systematic — usually hundreds or thousands of trades per day, with average durations measured in seconds, not minutes." |
| Sim-fill exploitation | prohibited; profits may be rejected | ts_10305426.html.txt | "Running scalping algorithms designed to exploit unrealistic SIM fills"; "Making hundreds of rapid trades to take advantage of preferential queue position in SIM"; "Using tight brackets or auto-breakeven to take advantage of favorable SIM fills"; "We retain the right to reject profit claims if abuse is suspected." |
| Orders outside the BBO | prohibited (wording could reach resting limit orders away from the touch; not defined further) | ts_10305426.html.txt; ts_10296582.html.txt | "Trading Outside the Best Bid or Offer" / "Placing orders at prices outside the current best bid or offer." |
| Price/feed exploitation | prohibited | ts_10296582.html.txt | "Price exploitation — strategies designed to exploit errors in price display or data feed delays"; "Using an external or slow data feed to trade" |
| Hedging, coordination | cross-account hedging and coordinated trading prohibited | ts_10296582.html.txt | "Cross-account hedging (single-user) — holding opposite positions across multiple accounts simultaneously" |
| Copier | allowed in Combine and XFA, not LFA | ts_14434175.html.txt | "Trade copying is only available for Trading Combine® and Express Funded Account® accounts." |
| Sessions | one concurrent session across devices | ts_14434175.html.txt | "Exchange regulations limit your access to one concurrent user session across all devices (PC, mobile, etc.)." |

Interpretation flags for the lead (not decisions): (a) a 20-round-trip/day strategy with ~1-minute holds is far from
the "hundreds or thousands of trades per day ... measured in seconds" description, but the Terms' "short term or
high frequency trades" example has no threshold; (b) "Placing orders at prices outside the current best bid or
offer" is undefined and could be read to cover passive limit orders resting behind the touch; (c) the API is not
available on Live, so automated trading ends at the XFA unless the trader moves to manual trading.

## 5. Platforms, sim fill rule, VPS

| Item | Value | Source | Quote |
|---|---|---|---|
| Platforms | TopstepX (web, desktop, mobile browser), Quantower via TopstepX credentials (Combine and XFA only), ProjectX API | ts_14434175.html.txt; ts_8284179.html.txt | "TopstepX™ is Topstep’s trading platform built for execution, risk management, and performance tracking."; "Quantower connects through TopstepX credentials. No API access needed."; "Quantower via TopstepX is available for the Trading Combine® and Express Funded Account® (XFA) only." |
| Platform owner | ProjectX Trading LLC | ts_www_home.html.txt | "It is developed and owned by ProjectX Trading LLC (“TopstepX”)." |
| Sim fill rule for resting limits | fills only when the market trades through the price, not on a touch; partial fills | ts_8765442.html.txt (2026-09-16) L72, L172 | "Price execution over speed. Trade-off: the market has to trade through your price — not just touch it. You might not get filled. Partial fills happen."; "Limit orders especially — if the market doesn't trade through your price, you don't get filled." |
| Sim realism claim | sim models slippage | ts_8765442.html.txt | "Simulated platforms model real market conditions, including slippage, to keep the experience realistic." |
| Data servers | Northern Virginia; orders run server-side | ts_14434175.html.txt | "Data servers sit in Northern Virginia, and every Trader connects there regardless of location for market data."; "order execution runs server-side, not through your browser." |
| Market data | Level 1 included; Level 2 USD 38/month | ts_14289835.html.txt; ts_8284197.html.txt | "$38/month"; "Level 1 (Top of Book) live data is included in your Topstep membership at no extra cost." |
| VPS | prohibited for order flow (section 4) | ts_11187768.html.txt | see section 4 |
| Sandbox | none; use the free Practice Account | ts_11187768.html.txt | "No. There is currently no sandbox environment available." |

Note: the "trade through" sentence sits in a general order-types article ("All order types below are available on
TopstepX™"); it is the firm's own description of limit fills on its platform, not a separate engine specification.

## 6. Reliability

| Item | Value | Source | Quote / note |
|---|---|---|---|
| Founding | Patak Trading Partners 2010; TopstepTrader launched 2012; LLC July 2012 | ts_www_about-us.html.txt L45-53; wiki_topstep.html.txt L108 (pointer) | "2010" "Founding of Patak Trading Partners"; "2012" "Launch of Topstep Trader" |
| Entities | TopstepTrader, LLC (Combine, XFA); TopstepFunded LLC (LFA, Illinois); Topstep Brokerage LLC (IB, NFA ID 0567079) | ts_www_about-us.html.txt L134; ts_terms_of_use.html.txt L44 | "Simulated trading program services, comprising the Trading Combine, and the Express Funded Account, and Topstep Labs experiments are operated by TopstepTrader, LLC"; "a registered introducing broker and a member of the National Futures Association. More information about the firm may be found here under NFA ID# 0567079." |
| Payout claims (firm's claims) | USD 1.5B+ paid all time (home); USD 1.4B+ (instant-payouts page); 99.26% approval; 9 s average instant payout; 7,000+ traders paid weekly | ts_www_home.html.txt L25-31; ts_www_instant-payouts.html.txt L18-23 | "$1.5B+" "Paid out to prop firm traders1"; "$1.4B+" "Paid out to traders1"; "99.26%" "Payout approval rate"; "9 seconds" "Average instant payout time*" (US/Aeropay RTP only) |
| Payout speed (policy) | internal approval 1-3 business days; Wise 1-3 business days; wire 5-10 | ts_8284233.html.txt | "Internal approval can take 1-3 business days." |
| 2025 statistics (firm disclosure) | 16.8% of Combines passed; 51.8% of participants reached funded; 33.3% of funded participants received a payout; 0.71% called up to Live | ts_www_about-us.html.txt L140 | "From January through December 2025, (a) 16.8% of all Trading Combines initiated were successfully completed ... (c) 33.3% of all individual participants at the Funded Level received a payout, and (d) 0.71% of individual participants trading in an Express Funded Account were called up to a Live Funded Account." |
| Regulatory actions against the firm | none found (CFTC, NFA, FTC, state AG) within budget | 3 WebSearch calls; NFA BASIC page is JavaScript-only (nfa_basic_0567079.html, no data) | negative result, not proof; NFA BASIC not readable by curl |
| NFA registration change | Topstep reportedly became an NFA member, Swap Firm and CTA in April-May 2026 [secondary press] | tradeinformer_topstep_cta.html.txt L92-96 (May 19, 2026) | "Prop trading firm Topstep has registered with the National Futures Association (NFA) as a Swap Firm and has also been approved to operate as a Commodity Trading Advisor (CTA)." Not verified on NFA BASIC. |
| Litigation (private) | McCrudden v. Topstepfunded LLC, M.D. Fla. 3:26-cv-00816, filed 2026-04-09, open; pro se; motions to compel arbitration (Jun 2026), mediator selected (Jul 2026); allegations include operating as an unregistered CPO [secondary press] and liquidations after reaching Live [snippet] | cl_search_topstep_recap.json; cl_docket_mccrudden.html.txt L117 | "COMPLAINT against All Defendants (Filing fee $405.00, receipt number 38733) filed by Vincent McCrudden.(ELA) (Entered: 04/10/2026)"; docket entries "Compel" (Jun 8 and Jun 30, 2026). Other: Footlick v. Topstep LLC, N.D. Ill. 1:22-cv-06152 (2022, contract) |
| Platform incidents | late-2025 TopstepX outages and failed SL/TP orders reported [pointer: Wikipedia citing a news site] | wiki_topstep.html.txt L122-124 | "In late 2025, Topstep, experienced a series of critical technical failures on its proprietary trading platform, TopstepX." Pointer only. |
| Payout disruption | Wise payouts suspended then restored for China, Canada, UK in August 2026 | ts_8284233.html.txt | "August 2026: Wise Payout Option Restored for Select Regions"; "Wise remains unavailable everywhere else." |
| Acquisition | The Futures Desk (2026) | ts_www_about-us.html.txt L136; wiki L131 (pointer) | "The Futures Desk is an online proprietary trading firm that evaluates and funds retail futures traders owned by TS TFD Buyer, LLC" |

### Rule changes in the 12 months to 2026-10-21 (evidence: Wayback copies of Oct 2025 vs today)

| # | Change | Before (source) | Now (source) | Direction (fact-level note) |
|---|---|---|---|---|
| C1 | XFA per-request payout cap at 50K | "Traders can request a payout of up to $5,000 or 50% of their account balance after accumulating five winning trading days" (wb2025_ts_8284233.html.txt L69, archived 2025-10-17) | 50K Standard USD 2,000, Consistency 3,000; doubled with DLL (ts_8284233.html.txt) | lower cap at 50K |
| C2 | Combine consistency | "Consistency Target: Best Day below 50% of total profits made" (wb2025_ts_8284197.html.txt L68, archived 2025-09-18) | 55% of profit target, "no buffer" (ts_8284208.html.txt) | looser threshold, buffer removed |
| C3 | Platforms | NinjaTrader, Quantower, Tradovate, TradingView named (wb2025_ts_8284197.html.txt L71) | TopstepX, Quantower via TopstepX, ProjectX API only (ts_14434175, ts_8284179) | fewer platforms |
| C4 | Daily Loss Limit | "Beginning Sunday, August 25th, 2024, any new or reset TopstepX™ accounts will be created without the Daily Loss Limit." (wb2025_ts_8284197.html.txt L70) | optional DLL at purchase with discounts and double caps (ts_10490293, ts_8284233) | new option |
| C5 | Back2Funded window | 7 days | 30 days from 2026-05-29 (ts_12060405.html.txt) | longer |
| C6 | Tier 1 news window | E.19 (2026-10-10) quoted "Topstep doesn't require you to flatten positions during economic releases — in SIM or Funded Accounts." | sentence removed; 10-minute window on equity index and metals, PPI added 2026-10-20 (E.26; ts_13613539) | new restriction |
| C7 | Volatility caps | not in Oct 2025 copies read | SI, HG, PL = 0; energies and gold capped (ts_13613539) | new restriction; start date not found |
| C8 | Double payout caps with DLL | - | from 2026-06-02, "No end date has been established" | promotional |
| C9 | Wise | - | restored Aug 2026 for Canada after a suspension | payout method disruption |

Wayback copies of the commissions page and of www.topstep.com/topstep-prop and article 13613539 could not be
fetched (connection failures, HTTP 000, logged); the Oct 2025 prices are therefore not compared.

## 7. Eligibility: British Columbia and Canada

| Item | Value | Source | Quote |
|---|---|---|---|
| Canada / BC | eligible (Canada is in neither the XFA-only list nor the ineligible list; no province is named) | ts_8284116.html.txt (2026-09-04) | "I'm Canadian — can I earn a Funded Account?" "Yes. You trade on a sub-account of Topstep's master account, considered a US-based account." |
| Basis | citizenship and permanent residency; OFAC and partner restrictions | ts_8284116.html.txt | "Eligibility is based on both citizenship and permanent residency. OFAC sanctions and partner restrictions apply." |
| Payout methods for Canada | Wise (no Topstep fee, 1-3 business days), Wire/SWIFT (USD 30, 5-10 business days); Aeropay and ACH are US only | ts_8284233.html.txt | "Wise is available again as a payout method for traders in China, Canada, and the United Kingdom." |
| Currency | not stated; Wise "supports local currency conversion" (fees are quoted in USD) | ts_8284233.html.txt | "Best for international Traders: Wise. Fastest, most cost-effective, and supports local currency conversion." |
| KYC | identity verification before the second purchase; government photo ID and selfie | ts_12578731.html.txt | "It's required before your second purchase and takes only minutes to complete." |
| Tax forms | W-8BEN for non-US persons | ts_8284233.html.txt; ts_8284238.html.txt | "W-9 for US persons, W-8BEN for non-US persons." |
| VPN | prohibited | ts_10296582.html.txt | "Do not use a VPN." |
| Terms | Illinois entities; Terms bar use where local law restricts such agreements | ts_terms_of_use.html.txt L70 | "If you are residing in a jurisdiction that restricts the ability to enter into agreements such as set out in these Terms of Use, you may not enter into this agreement" |

Canadian tax treatment: not covered by any Topstep page beyond the W-8BEN form (not researched here).

## 8. Differences between the E.19 rules record and today's pages

Record checked: `reports/stage_e19_rules.json` as on disk today (schema e19-rules-1, 234 rules R001-R234 and 42
practices; it includes E.26's refresh of 2026-10-21 02:20 PDT: R040 re-sourced, R215-R234 added, sources S42-S44).
Method (`work/A2_topstep/A2_topstep_e19diff.py`, output `work/A2_topstep/A2_topstep_e19diff.tsv`): for every rule
and practice, the quote was searched in today's copy of its source page after normalising whitespace, table pipes,
quotes and dashes. Then every source page whose dateModified changed since E.19 was diffed sentence by sentence
(`work/A2_topstep/A2_topstep_linediff.py`).

Quote check result: 243 FOUND; 2 flagged and resolved by hand as not substantive (R060: today reads "(DLL):"
where E.19 had "(DLL ):", a spacing change; R224: a multi-row table quote joined by ";" that the script does not
split, all five rows are present today); 31 not checkable as text (24 scaling-plan rules on S40, an image that is
byte-identical today, sha256 55ec76b4b293...; 7 UNSOURCED rules with no quote). **No E.19 quote has disappeared and
no recorded value is contradicted by today's pages.**

Pages changed since E.19 (dateModified E.19 -> today) and what changed:

| Source | Page | dateModified | Substantive change today | Effect on the record |
|---|---|---|---|---|
| S06 | Pricing and Payment (14289835) | 2026-09-25 -> 2026-10-15 | New "Affiliate Codes" section: "When someone purchases with Topstep for the first time using an affiliate code, they save 20%."; "Affiliate codes do not apply to Resets, Back2Funded, market data add-ons, or anything you buy after that first purchase." | not in the record (first-purchase discount only); prices unchanged |
| S08 | Combine Subscriptions (8284121) | 2026-09-04 -> 2026-10-12 | Added: "Payments already processed for the current billing cycle are not refunded or prorated." and "the passed Trading Combine remains in "Passed" status until you activate your Express Funded Account" | not in the record; the first confirms no pro-rata refund of the month in which the Combine passes |
| S17 | Payout Policy (8284233) | 2026-09-30 -> 2026-10-13 | Added a Consistency-path example and: "Profits from the previous cycle remain in your account balance but do not count toward the new cycle’s Consistency Target calculation." | consistent with R099-R104; supports INFERRED R104 indirectly |
| S20 | LFA Parameters (10657969) | 2026-10-01 -> 2026-10-20 | no sentence-level change found | none |
| S22 | Economic Releases (8284211) | 2026-09-10 -> 2026-10-15 | flatten sentence removed (already handled by E.26, R040) | handled |
| S28 | LFA costs (8284229) | 2026-06-16 -> 2026-10-19 | only the date marker differs | none |
| S31 | RTP (13620045) | 2026-10-01 -> 2026-10-15 | wording only ("If passed, the Trading Combine may be activated as either a Standard XFA or Consistency XFA.") | none |
| S32/S42 | Risk Adjustments (13613539) | 2026-10-08 -> 2026-10-20 | identical to E.26's copy (same sha256 085db4d216de...); E.26 covered the Tier 1 section | see below |
| S35-S39 | www rules and promo pages | unchanged "Last updated" dates | whitespace only | none |

Facts on today's pages that the E.19 record does not carry (gaps, not contradictions):

1. Per-product commissions and fees (section 2); the record has no commission field. The LFA costs page's
   "$3.70/lot simulated fee" in the Combine conflicts with the product table.
2. The volatility restrictions outside the Tier 1 section (13613539, "Current Restrictions"): SI, HG, PL = 0 at all
   sizes; CL, QM, RB, HO, GC = 3 and MCL, MGC = 30 at 50K; SIL, MHG = 2 at 50K; the XFA ceiling rule for these
   products. R218 lists SI, HG and PL among Tier 1 "mini products" although they are currently at 0 anyway.
3. The permitted product list and the products absent from it (ETH, BTC, micro yields, micro and mini grains).
4. CBOT grain and CME livestock special hours, the 3:08 PM CT flattening start, and the holiday rule (flat 15
   minutes before an early close). The record has the 3:10 PM CT flat-by (R032) and the 5 PM start (R031).
5. The ProjectX API rate limit (200 requests per 60 s) and bracket modes; the API's unavailability on Live is in
   the record (R020).
6. The sim limit-fill rule ("trade through your price — not just touch it").
7. (Not a gap: the record already carries "Placing orders at prices outside the current best bid or offer." as
   practice P05, the SIM-fill practices as P07-P11, the Terms' short-term/high-frequency clause as P16 and the VPS
   ban as P26; all 42 practice quotes are still present today.)
8. The SIL counts-as-2 and MBT/MET mini-equivalent scaling exceptions.

E.19 CONFLICT items, re-checked today: R025 (DLL at a new Combine purchase needed for double caps) still stands:
today's payout page says "Only if you already added the DLL when you purchased your Trading Combine." while the
T&C page says "traders who add a Daily Loss Limit (DLL) to their Topstep account will unlock double the standard
payout caps". R058 (minimum payout balance after the first payout) still stands: the www XFA rules page (Last
updated June 26, 2025, unchanged) still says "After the first payout, a Minimum Payout Balance must be met for
subsequent payouts." while the help centre requires only "at least $0.01 since your last Payout". R029 (55%
inclusive or strict) still stands: 8284208 "at or below 55%", 8284197 "keep your best day below 55%".

Stale www page: `www.topstep.com/express-funded-account-rules` (Last updated June 26, 2025) still states a USD
5,000 Standard cap at all sizes and a 7-day Back2Funded window; the help centre (50K cap 2,000; 30 days) is newer.

## 9. Not found, not verified, deviations

- No deviation fetches; no Scrapling or Firecrawl; no DO_NOT_COMMIT pages (topstep.com terms do not forbid
  targeted retrieval; Justia blocked curl with a Cloudflare challenge and was not used).
- NFA BASIC (JavaScript-only) could not be read; Topstep's NFA status and any NFA actions are unverified.
- CFTC, FTC and state AG actions: none found in 3 searches; this is a negative search result, not a clearance.
- Wayback copies of the commissions page, the www pricing page and article 13613539 for Oct 2025 failed (HTTP 000).
- The meaning of the asterisks on the product list is undocumented on the pages read.
- Payout currency for Canada is not stated.
- The McCrudden complaint text was not read (PACER); allegations are from secondary press and a search snippet.
- WebSearch calls used: 6 of 40.
