# A2_firm_lucid: Lucid Trading, Layer 2 firm facts (lookup date 2026-10-21)

Worker: A2_lucid (Stage E.28). Facts only, no scores. Spec: reports/stage_e28_ranking_spec.md section 3.
Saved pages: reports/stage_e28_briefs/pages/A2_lucid/ (log.tsv has URL, UTC and PDT fetch times, method, sha256).
Machine-readable copy: reports/stage_e28_briefs/A2_firm_lucid.json.

## 0. Access route, terms decision, and how current the facts are

- Terms: the Lucid Terms of Use (E.13 copy reports/stage_e13_briefs/pages/PropVenues2/lucid_tou.txt line 138; Wayback
  copy pages/A2_lucid/lucid_tou_wb.html.txt line 78, "Last Modified: March 20, 2025") say: "Use any robot, spider, or
  other automatic device, process, or means to access the Website for any purpose, including monitoring or copying any
  of the material on the Website." Decision (logged first in log.tsv): no curl, Scrapling or Firecrawl on
  lucidtrading.com or support.lucidtrading.com (the site's FAQ link points at the help centre, so it is treated as
  covered). Routes used: Wayback Machine copies (curl to web.archive.org), WebSearch summaries (marked [snippet]),
  and deviation fetches (one WebFetch per page) where the fact could only come from today's page.
- Deviation fetches (listed in pages/A2_lucid/DO_NOT_COMMIT.txt):
  1. support.lucidtrading.com/en/articles/11508978-approved-products-and-commissions, 2026-10-21 ~06:00 PDT, WebFetch:
     succeeded; the table matched the 2026-09-22 Wayback copy row for row (dev_products_commissions_webfetch_20261021.txt).
  2. lucidtrading.com/ (pricing), 2026-10-21, WebFetch: HTTP 403, no body. Today's pricing page could not be read.
     The latest Wayback copy with status 200 is 2026-10-05 20:04:51 UTC (a 2026-10-10 Wayback capture also got 403).
- Firecrawl: the connector returned "Insufficient credits" on 2026-10-21 (first call), so it was not used. Logged.
- Dates: each fact gives the Wayback capture date (UTC) and, for help-centre articles, the Intercom
  "lastUpdatedDate" stored in the page. Most rule articles were captured 2026-10-07 to 2026-10-20 and were last
  updated on or before 2026-08-26. The E.13 copies (fetched 2026-10-03, reports/stage_e13_briefs/pages/PropVenues2/)
  of LucidPro Evaluation, HFT and Other Trading Activities carry the same lastUpdatedDate and text as today's copies.
- Quote format: table rows are quoted with " / " between cells (the page puts each cell on its own line). Every JSON
  quote was checked by script against its source file (140 checked, 0 missing, ignoring whitespace and the " / ").
- Gap: a rule changed between a page's capture date and 2026-10-21 would be missed. The pricing page is the
  biggest risk (16 days old).

## 1. The standard 50K plan: LucidPro 50K (evaluation, then LucidPro Funded, sim)

Plan choice under the spec rule ("the first 50K evaluation plan on its pricing page"): the pricing widget config
on the homepage (lucid_home_wb.html, Wayback 20261005200451, script `LucidPricingConfig`) lists plan types in this
order: LucidPro (order 10), LucidFlex (20), LucidDaily (30), LucidDirect (40, straight-to-funded, no evaluation).
Quote: `"id":"pro","slug":"lucidpro","label":"LucidPro","headerSuffix":"PRO EVAL","order":10,"enabled":true`.
So the standard plan is **LucidPro 50K**. The visible text list on the same page puts "Lucidblack eval 50k" first, but
those are platform-selector labels (LucidBLACK sits in the "LucidBLACK (legacy)" help collection and is not a plan type
in the config). Lead to confirm this reading.

### 1a. Evaluation (LucidPro 50K)

| Item | Value | Source (file; capture; quote) |
|---|---|---|
| Price | USD 172, one-time (no monthly billing), DLL ON version | lucid_home_wb.html (2026-10-05): spec `"id":"one_time_fee","label":"One Time Fee"` cell s50k = product `1661`; `"productPrices":{... "1661":"172"`. Billing: sup_sim_fees.html.txt (updated 2026-08-26): "LucidPro Evaluation and LucidDirect accounts are purchased by paying a one-time fee. There is no subscription and no automatic rebilling." |
| DLL-OFF version | USD 172 + 20 = 192 (inference from config) | `"addonFees":{"56539":15,"1661":20`; addon `"slug":"no-dll","label":"Daily Loss Limit"`. sup_pro_custom.html.txt: "Daily Loss Limit Off ... Results in a higher evaluation purchase price". The +20 reading of `addonFees` is my inference. |
| Discount | Config gives `"discountPct":30` for every size and `"couponCode":"VAULT"`; page text "FOR THE BEST DEAL USE CODE : VAULT". 172 x 0.70 = 120.40 if the 30% applies (inference, not stated as a price) | lucid_home_wb.html |
| Reset fee | USD 120 (DLL ON); +20 for DLL OFF (inference) | reset spec cell s50k = product `9789`; `"9789":"120"`; `"addonFees"... "9789":20`. sup_sim_fees: "Resets are not automatic or free." |
| Activation fee | None | config meta `"label":"Account Activation Fee:","value":"FREE"`; sup_sim_fees: "There is no activation fee to upgrade a LucidPro Evaluation to a LucidPro Funded." |
| Profit target | USD 3,000 | sup_pro_eval.html.txt (capture 2026-10-07, updated 2026-08-26) table row "$50,000 / $3,000 / $2,000 / $1,200 / 4 mini or 40 micros" |
| Max loss limit | USD 2,000, end-of-day trailing; trails the highest EOD closing balance until the balance exceeds the Initial Trail Balance USD 52,100, then locks at USD 50,100 | sup_pro_drawdown.html.txt (capture 2026-10-20, updated 2026-08-26): "LucidPro evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system"; "Once your account exceeds the Initial Trail Balance, the MLL locks and no longer moves"; row "$50,000 / $2,000 / $52,100 / $50,100"; "If your account balance reached the MLL, your account will be breached." |
| Daily loss limit | USD 1,200 fixed, soft (lockout until next session, account not failed); optional (DLL OFF plan has none) | sup_pro_dll.html.txt (capture 2026-10-20, updated 2026-07-26): "All DLLs at Lucid Trading are considered soft breaches, meaning you do not lose your account for hitting DLL as long as the Max Loss Limit (MLL) has not been reached."; "$50,000 / $1,200" |
| Consistency rule (eval) | None published for LucidPro eval (LucidFlex and LucidDaily evals have 50%) | Pro front specs in config have no consistency row; Flex and Daily do (`"consistency"` cell s50k "50%"). sup_pro_eval lists none. |
| Minimum days | None (can pass in one day) | sup_pro_eval: "Pass the evaluation in one trading day" |
| Time limit | None, but inactivity deletes accounts after 30 days without a USD 1 net P&L | sup_pro_eval: "One-time fee, no monthly rebilling, take as long as you need to pass"; sup_inactivity.html.txt (updated 2026-08-26): "Accounts that have not been traded resulting in at least a net profit or loss of 1$ within 30 calendar days will be deemed abandoned and will be permanently deleted" |
| Max size | 4 minis or 40 micros (ratio 1:10) | sup_pro_eval row; config `"max_size"` "4 Mini OR 40 Micro" |
| Activation timing | 5 to 30 minutes after hitting target | sup_pro_eval: "Real time activation, upgrade to funded account within 5-30 minutes of hitting profit target" |

### 1b. Funded stage (LucidPro Funded 50K): simulated

| Item | Value | Source |
|---|---|---|
| Sim or live | Simulated ("sim funded"); live is a later discretionary move | sup_pro_funded.html.txt (capture 2026-10-07, updated 2026-08-26): "The LucidPro funded account is a simulated account where traders build simulated capital to earn payouts and potentially be moved to live markets." |
| Drawdown | USD 2,000 EOD trailing, same lock as eval (locks at 50,100 once above 52,100) | sup_pro_drawdown (as above); sup_pro_funded row "$50,000 / $2,000 / $1,200 / 60% of Peak EOD Balance / 4 mini or 40 micros" |
| Daily loss limit | Fixed USD 1,200 while balance is below 52,100; after the account closes above 52,100 it becomes the LucidScale DLL = 60% of the highest EOD profit, never decreasing; soft; optional (OFF plan: none) | sup_pro_dll: "Once the account closes above the Initial Trail Balance, the Fixed DLL is replaced by the LucidScale DLL." "Highest end-of-day account profit × 60% = LucidScale DLL"; "It does not decrease, even if the account draws down" |
| Profit split | 90% trader / 10% Lucid (accounts bought or reset from 2025-11-28 15:00 EST) | sup_pro_payouts.html.txt (capture 2026-10-20, updated 2026-08-06): "All funded account payouts are split 90% to the trader and 10% to Lucid Trading. Accounts purchased or reset before 11/28/2025 at 3:00 PM EST are still eligible for 100% on the first $10k." |
| Minimum profit per cycle | USD 500 between payouts (resets each payout) | sup_pro_payouts: "$50,000 / $500"; "This profit goal resets after each payout." |
| Consistency (funded) | Largest single day profit <= 40% of cycle profit; resets each payout | sup_pro_payouts: "Your largest single-day profit must be no more than 40% of your total profit during the payout cycle." sup_pro_consistency: "Largest Single Day Profit / Account Profit = Consistency Percentage" |
| Buffer | Profit must exceed buffer = initial MLL + USD 100, i.e. balance above 52,100; no withdrawal from the buffer | sup_pro_payouts: "The buffer is equal to: Initial Max Loss Limit + $100"; "You can not take payout from the buffer balance." Table "$50,000 / $52,100 / $500 / $52,600 / $2,000 / $54,100" |
| Payout min / max | Minimum request USD 500; maximum USD 2,000 for payout 1, USD 2,500 for payouts 2+ (50K) | sup_pro_payouts: "Minimum payout request: $500"; Payouts 2+ row "$50,000 / $52,100 / $500 / $52,600 / $2,500 / $54,600" |
| Minimum days to payout | 3 (pricing config); help article names no day count, but 40% consistency implies at least 3 profitable days | config `"label":"Days to Payout","kind":"text","cells":{"s25k":"3","s50k":"3","s100k":"3","s150k":"3"}` (Pro funded) |
| Frequency | Any day once criteria are met; disbursed within 2 business days | sup_pro_payouts: "There is no fixed payout window, you may request a payout any day after meeting all eligibility criteria." "Payouts will be disbursed to your payment method within 2 business days." |
| Number of sim payouts | Payout 5 is the maximum payout level on Pro/Flex/Direct; then the trader enters the live review pool | sup_new_live.html.txt (capture 2026-10-16, updated 2026-10-14): "After receiving the final payout (Payout 5) on their Flex, Pro, or Direct plan"; "Payout 5 represents the maximum payout level, not a guaranteed minimum for live eligibility. This maximum payout level applies to Flex, Pro, and Direct plans." The Pro payouts page itself states no cap on the number of payouts. |
| Payout caps | "No simulated payout caps" (per Pro funded page) beside the per-payout maxima above | sup_pro_funded: "No scaling plan, access to max contract size immediately"; "No simulated payout caps" |
| Scaling plan (sim funded) | None: full 4 minis / 40 micros from day 1 | sup_pro_funded (quote above); config Scaling Plan cell "—" |
| Max accounts | 5 funded per household (all funded types combined); 10 evaluations; 10 total | sup_max_accounts.html.txt (updated 2026-08-26): "Up to 5 active funded accounts per household or family."; "Up to 10 active evaluation accounts per household or family."; "Traders may hold a maximum of 10 accounts in total across evaluation accounts and funded accounts." |
| Payout request mid-trade | Request may be denied if balance falls into buffer before processing | sup_pro_payouts: "If you trade after submitting but before approval and your balance drops into the buffer, the request may be denied." |

### 1c. Live stage (for the funnel's end state)

sup_new_live.html.txt (updated 2026-10-14): live is at the risk team's discretion ("All live transitions occur at the
discretion of the Lucid risk team"); "Each funded account must have received at least one payout to qualify"; live
accounts begin with "$0 starting balance", "Daily payouts", "End of Day (EOD) drawdown", "No daily loss limit"; 50K row
"$50,000 / $2,000 / 4 minis or 40 micros". A cashout alternative: "This cashout option is equal to 50% of a traders live
starting balance and is subject to a 90/10 profit split." On going live, "All simulated prop accounts are closed".
Live MLL "locks at $100" once live profits equal the starting live drawdown. Live bonus at 50K: USD 4,000 live profit
plus 20 trading days gives a USD 2,000 bonus (90/10). Live cooldown after a blown live account: "Standard cooldown
period: 2 weeks". Live scaling (sup_live_scaling.html.txt, updated 2026-10-04), 50K: USD 0-1,999.99 profit: 2 minis or
20 micros (CME, CBOT, NYMEX), 1 mini or 10 micros (COMEX); 2,000-3,999: 3/30 (COMEX 1 mini or 15 micros); 4,000+: 4/40
(COMEX 2 minis or 20 micros). Live flat time: "Traders may hold positions until 4:45 PM EST on Tradovate Live accounts,
or 4:15 PM EST on Rithmic Live accounts" (sup_trading_times). Household rule: "If one household member is trading live,
others may not trade simulated accounts."

### 1d. Mapping notes for a Combine-to-funded funnel simulator (facts restated, no choices made)

- Eval: start 50,000; pass when balance >= 53,000 (target 3,000); fail when balance <= MLL, MLL = max(48,000,
  highest EOD close - 2,000), capped at 50,100 once an EOD close exceeds 52,100. Whether the intraday breach test uses
  open P&L is not stated (page says "If your account balance reached the MLL"); the conservative form is intraday
  equity. DLL 1,200 is soft: stop the day, keep the account. No minimum days, no eval consistency, no time limit
  (30-day inactivity aside). Fee 172 per attempt; a reset (120) restarts a failed eval; no activation fee.
- Funded (sim): same MLL rule restarting from 50,000. Payout when: cycle profit >= 500, max day <= 40% of cycle profit,
  balance > 52,100, request >= 500; amount <= min(balance - 52,100, 2,000 for payout 1, 2,500 after); trader gets 90%.
  Days to payout 3. At most 5 payouts, then the account leaves the sim funnel (live review or cashout, discretionary).
  DLL 1,200 below 52,100, then 60% of peak EOD profit.

## 2. Products, commissions and position limits

Source: sup_products_commissions.html.txt (Wayback 2026-09-22; Intercom lastUpdatedDate 2026-08-26T21:08:23Z) and
deviation fetch dev_products_commissions_webfetch_20261021.txt (2026-10-21, identical). Intro: "Futures products
approved for trading at Lucid Trading and the commission rates per contract". Column header: "Commission (Per Side)".
The page does not say whether exchange and NFA fees are included; it gives one number per side and no separate fee
column, so the lead may treat it as all-in (assumption, not stated). Round trip below = 2 x per side (my arithmetic).
A product not in the table is not approved (the table is titled as the approved list).

| Code | Allowed | Per side USD | Round trip USD | Quote (row as on page) |
|---|---|---|---|---|
| MNG | no (not listed) | - | - | - |
| QG | yes | 1.30 | 2.60 | "QG / E-mini Natural Gas Futures / 1.30 / NYMEX" |
| NG | yes | 2.00 | 4.00 | "NG / Henry Hub Natural Gas Futures / 2.00 / NYMEX" |
| MCL | yes | 0.50 | 1.00 | "MCL / Micro Crude Oil / 0.50 / NYMEX" |
| QM | yes | 2.00 | 4.00 | "QM / E-mini Crude Oil Futures / 2.00 / NYMEX" |
| CL | yes | 2.00 | 4.00 | "CL / Crude Oil Futures / 2.00 / NYMEX" |
| MGC | yes | 0.80 | 1.60 | "MGC / Micro Gold Futures / 0.80 / COMEX" |
| GC | yes | 2.30 | 4.60 | "GC / Gold Futures / 2.30 / COMEX" |
| SIL | yes | 1.60 | 3.20 | "SIL / Micro Silver / 1.60 / COMEX" |
| SI | yes | 2.30 | 4.60 | "SI / Silver / 2.30 / COMEX" |
| MHG | no (not listed) | - | - | - |
| HG | yes | 2.30 | 4.60 | "HG / Copper Futures / 2.30 / COMEX" |
| M6E | no (not listed) | - | - | - |
| 6E | yes | 2.40 | 4.80 | "6E / Euro FX Futures / 2.40 / CME" |
| M6A | no (not listed) | - | - | - |
| 6A | yes | 2.40 | 4.80 | "6A / Australian Dollar Futures / 2.40 / CME" |
| MET, ETH, MBT, BTC | no (no crypto listed) | - | - | - |
| M2K | yes | 0.50 | 1.00 | "M2K / Micro E-mini Russell 2000 Index Futures / 0.50 / CME" |
| RTY | yes | 1.75 | 3.50 | "RTY / E-mini Russell 2000 Index Futures / 1.75 / CME" |
| MYM | yes | 0.50 | 1.00 | "MYM / Micro E-mini Dow Jones Industrial Average Index Futures / 0.50 / CBOT" |
| YM | yes | 1.75 | 3.50 | "YM / E-mini Dow ($5) Futures / 1.75 / CBOT" |
| MNQ | yes | 0.50 | 1.00 | "MNQ / Micro E-mini Nasdaq-100 Index Futures / 0.50 / CME" |
| NQ | yes | 1.75 | 3.50 | "NQ / E-mini Nasdaq-100 Futures / 1.75 / CME" |
| 2YY, 5YY, 10Y, 30Y | no (no rates listed) | - | - | - |
| ZT, ZF, ZN, ZB | no (no rates listed) | - | - | - |
| micro grains (MZC, MZS, MZW, MZL, MZM) | no (not listed) | - | - | - |
| XC, XK, XW | no (not listed) | - | - | - |
| ZC | yes | 2.80 | 5.60 | "ZC / Corn Futures / 2.80 / CBOT" |
| ZS | yes | 2.80 | 5.60 | "ZS / Soybean Futures / 2.80 / CBOT" |
| ZW | yes | 2.80 | 5.60 | "ZW / Chicago SRW Wheat Futures / 2.80 / CBOT" |
| ZL | yes | 2.80 | 5.60 | "ZL / Soybean Oil Futures / 2.80 / CBOT" |
| ZM | yes | 2.80 | 5.60 | "ZM / Soybean Meal Futures / 2.80 / CBOT" |

Other approved products (outside the candidate list): ES 1.75, MES 0.50, NKD 1.75, 6B, 6C, 6J, 6S, 6N 2.40, PL 2.30,
HE 2.80, LE 2.80. 34 rows in all.

Position limits at 50K (eval and sim funded): 4 minis or 40 micros, ratio 1 mini = 10 micros (sup_pro_eval,
sup_pro_funded). No product-specific reduction is published for the sim stages; the live stage reduces COMEX metals
(see 1c) and says "Certain extremely volatile contracts have reduced position sizing" (sup_new_live). The hedging page
allows long minis and short micros of the same product in one account: "You can go long / short the same contract but one
is micros and one is minis in the same account." (sup_hedging.html.txt, capture 2026-10-20, updated 2026-10-06).

## 3. Product restrictions, news windows, trading hours

- News trading on LucidPro: allowed, no window. sup_other_activities.html.txt (capture 2026-10-07, updated
  2026-08-26): "News Trading / Not allowed on Daily / Trading red folder news on the LucidDaily is a hard breach /
  Allowed on Flex, Pro and Direct / Traders may enter or exit positions around scheduled or unscheduled news events on
  these plans without it being a breach". No event list or window length is given for LucidDaily either.
- Product-specific restrictions in the sim stages: none found. Live stage: COMEX size reduction (1c).
- Flat-by time: sup_trading_times.html.txt (capture 2026-10-07, updated 2026-08-26): "All positions must be closed by
  4:45 PM EST, Monday through Friday"; "Any open positions will be automatically closed by Lucid Trading at 4:45 PM
  EST"; "Important: Holding a position past this time does not result in a failed account"; "Trading resumes at 6:00
  PM EST, Sunday through Thursday"; "On market holidays with altered closing times, all positions must be closed before
  the market closes, regardless of the usual 4:45 PM cutoff". So 16:45-18:00 ET (13:45-15:00 PT) is closed, against
  CME Globex's own 17:00-18:00 ET break: 15 extra minutes a day (my arithmetic). "EST" is written all year; whether
  it means ET is not stated.

## 4. Automation, API, order-rate and holding rules

- Automation permitted (firm-wide rules article; no evaluation or funded distinction made): sup_other_activities:
  "Automated Strategies / Automated trading systems and trade copiers are permitted / All automated activity must
  comply with Lucid Trading rules / Traders are fully responsible for any software errors, malfunctions, or unintended
  outcomes". The general FAQ (lucid_general_faq_wb.html.txt, Wayback 2026-07-13) says: "Are EAs/bots allowed? Copy
  trading? Automated strategies and in-platform/third party trade copiers are permitted, but traders are responsible for
  any software errors or unintended outcomes."
- Which API: no Lucid page read names an API (Tradovate API, Rithmic R|API, ProjectX/TopstepX or NinjaTrader).
  No saved page contains "API", "VPS" or a rate limit (grep over all pages). Automation runs through the supported
  platforms (section 5). [snippet] WebSearch summaries say Lucid supports "API access for Python, Java, and C++"
  (traderspost.io) and that "ProjectX is not supported anymore for LucidFlex accounts as of late 2025"
  (proptradingvibes.com). Both are secondary, not verified.
- HFT: banned, defined qualitatively, no number. sup_hft.html.txt (capture 2026-10-20, updated 2026-08-26):
  "High-frequency trading (HFT) is a type of automated trading strategy that involves submitting and executing a high
  volume of trades within extremely short time frames, often measured in seconds or even milliseconds."; "HFT
  strategies can result in hundreds of orders being placed within minutes"; "First offense: You will receive a written
  warning"; then "All profits generated from HFT activity will be removed / Accounts will be closed".
- Microscalping, a numeric minimum-hold test: sup_microscalping.html.txt (capture 2026-10-20, updated 2026-08-26):
  "You will be flagged if: More than 50% of your profits are generated from trades held for 5 seconds or less";
  "Genuine scalping is permitted as long as it reflects realistic market activity and order execution." Unchanged
  since the 2026-03-30 Wayback copy (sup_microscalping_wb_20260330.html; only headings differ).
- Scalping and flipping: sup_other_activities: "Genuine scalping is allowed"; "Scalping is considered valid as long as
  trades are taken in good faith and not intended to manipulate fill logic"; "Flipping is allowed".
- Hedging across accounts or firms: banned (sup_hedging): "Lucid Trading strictly prohibits all forms of hedging".
- **Exploiting simulated fills, exact quotes:**
  - Terms of Use (lucid_tou_wb.html.txt line 58, Wayback 2026-06-10, Last Modified March 20, 2025): "While utilizing
    the Website, Software, and Services, taking advantage of the simulated environment to gain an edge is not
    permitted. Trading activity that is knowingly or unknowingly circumventing targets and rules or generates profits
    that could otherwise be achieved in live market trading is a violation of the Terms of Use." (The last clause
    reads "could otherwise be achieved", which seems to mean "could not"; quoted as written.)
  - Terms of Use line 64: "Using any trading strategy intended to exploit or create errors in the Website, Services
    and/or Software such as errors in the display of prices or delay in their updates." Line 65: "Using any trading
    strategy that includes disruptive practices (as determined in Lucid’s sole discretion, including but not limited
    to spoofing strategies, microscalping, hedging, and high frequency trading."
  - Trade With Integrity (sup_integrity.html.txt, capture 2026-10-07, updated 2026-08-26): "Lucid Trading strictly
    prohibits the use of strategies that exploit platform mechanics or simulated market conditions." Examples:
    "Taking advantage of system errors or update delays", "Exploiting discrepancies in simulated prices", "Using
    tactics that do not reflect real-world trading conditions".
  - Microscalping page: "The goal is typically to exploit how simulated fills work rather than to execute a
    sustainable trading strategy."
  - Penalty clause (TOU line 85): Lucid may "remove the transactions that violate the prohibition from your trading
    history and/or not count their results in the profits and/or losses achieved by such simulated trading".
- A 20 round-trip-per-day, about 1-minute-hold strategy against these rules: holds of ~60 s are well past the 5 s
  microscalping test; 40 fills a day is far from "hundreds of orders ... within minutes". No published order-rate
  limit exists to test against (fact restatement; the A score is the lead's).

## 5. Platforms, sim fill rule, VPS

- Platforms (sup_platforms2.html.txt, capture of 11404614-lucid-trading-supported-platforms, updated 2026-07-28):
  "All listed platforms work with all Lucid account types." "CQG supported platforms: NinjaTrader / Tradovate /
  TradingView"; "Rithmic supported platforms: MotiveWave (Lucid Partner) / Quantower (Lucid Partner) / Tradesea /
  Sierra Chart / Jigsaw / Bookmap / ATAS / R|Trader Pro (official Rithmic platform) / MultiCharts". Homepage notice:
  "Accounts using Rithmic are activated on Sunday prior to 5PM CST". The pricing config pins `"platform":"rithmic"`
  as the default for each plan.
- Sim fill rule for resting limit orders: not documented on any Lucid page read (rules, platforms, FAQ, TOU). The
  firm tells traders about "velocity logic" and slippage around news (sup_other_activities) but gives no fill model.
  [snippet, forum pointer only] an Optimus Futures community thread quotes Rithmic: "Rithmic's Paper Trading system has
  an exchange simulator that fills orders based upon live market data. Our filling algorithm also takes into account
  when your order was received by the simulator, Rithmic's estimated place of the order in the order queue." Not
  fetched or verified, and not Lucid's statement.
- VPS: no Lucid page read mentions VPS, VPN or IP rules; one WebSearch found nothing first-party. Unknown.
- API rate limit: none published (unknown).

## 6. Reliability

- Operating history: less than 2 years. The domain was "for sale" in the 2024-09-01 Wayback copy
  (lucid_home_wb_20240901092035.html: "The domain name LucidTrading.com is for sale."); on 2025-02-20 it was a
  waitlist page (lucid_home_wb_20250220204435.html: "Coming Soon – Lucid Trading ... Sign up now to join our waitlist
  and receive our exclusive launch discount."). Footer: "@2024-2026 Lucid Trading. All rights reserved." Operator:
  "Lucid Trading Group LLC" (TOU line 24), address "3500 S Dupont Hwy Dover DE 19901" (homepage). Earliest help-centre
  capture is 2025-07-20. [snippet] secondary sites give "founded in April 2025" (pipback) or "July 2025"
  (fundedtrading.com).
- The firm's own claims (homepage, 2026-10-05; unaudited): "$700M+ earned by traders", "500K+ traders in the
  trenches", "15ish min from request to bank". FAQ: "typically within 5–15 minutes for Plaid, or up to 2 business days
  if international." Lucid publishes no pass or payout rates (E.25 R8 also found none).
- Disputes (pointers only, not evidence): WebSearch summaries of Trustpilot and PropFirmMatch reviews describe
  account closures citing Terms of Service violations after payout approval, KYC locks at the first payout, and a
  denial for "coordinated trading activity between users" [snippet]. Also positive reviews about fast payouts. No
  count and nothing verified.
- Regulatory actions against the firm: none found. Searches: WebSearch (CFTC, NFA, FTC, attorneys general, 2026) and
  Firecrawl government search ("Lucid Trading Group LLC ... enforcement") returned no action naming Lucid Trading. The
  "Lucid lawsuit" hits concern Lucid Motors. NFA BASIC and state AG sites were not queried directly (gap). Against
  peers, a WebSearch summary pointed to a trader's federal suit against Topstep [snippet].
- Rule changes in the 12 months to 2026-10-21 (from firm pages; the lead judges which are material and adverse):
  1. 2025-11-28: profit split for new or reset accounts went from 100% of the first USD 10k to a flat 90/10
     (sup_pro_payouts quote in 1b).
  2. 2025-11-28: LucidPro funded consistency 35% to 40%, a loosening (sup_pro_consistency: "We adjusted the LucidPro
     funded consistency percentage from 35% to 40%. It applies only to accounts purchased or reset on or after
     11/28/2025 at 3:00 PM EST.").
  3. Price: the 2025-11-01 homepage (lucid_home_wb_20251101.html, `lucidTestPlans`) shows the 50K evaluation that led
     to LucidPro at `value: "$135", strikethrough: true, label: "One Time Fee"` with `"Reset Fee", value: "$90"`; on
     2026-10-05 LucidPro 50K is USD 172, reset 120 (same target 3,000, MLL 2,000 EOD, DLL 1,200, 4/40). The 135 was
     shown struck through (a pre-discount list price), so the like-for-like rise is 135 to 172 list.
  4. Plan line-up: LucidBLACK moved to a "LucidBLACK (legacy)" collection; LucidDaily added; LucidMaxx added
     (invite-only); a new Live structure (updated 2026-10-14) with a legacy one beside it; new LucidLive accounts allow
     no swing trading (sup_trading_times: "Swing trading is not allowed in the new LucidLive accounts").
  5. News: the article version last updated 2025-08-26 (sup_permitted_activities.html.txt, Wayback 2026-07-15) said
     "News Trading / Allowed without restriction"; the version updated 2026-08-26 adds "Not allowed on Daily"
     (LucidPro unchanged). So the change came between 2026-07-15 and 2026-08-26.
  6. Payout caps for LucidPro unchanged between the 2026-03-04 copy (sup_pro_payouts_wb_20260304.html: payout 1 2,000,
     payouts 2+ 2,500 at 50K) and today. The "Payout 5" maximum appears in the Live page updated 2026-10-14; when it
     started is unknown.
  7. [snippet] ProjectX dropped for LucidFlex "as of late 2025"; crypto payouts stopped for China, Hong Kong, Taiwan,
     Singapore and Malaysia from 2026-08-26. Secondary, not verified.

## 7. Eligibility: British Columbia and Canada

- Canada is not on the restricted list (sup_restricted_countries.html.txt, capture 2026-10-20, updated 2026-10-08):
  "If you are a citizen or resident of any of the countries listed below, you are not eligible to use Lucid Trading
  services:" (list runs Afghanistan to Zimbabwe; Canada absent; no province-level rule). No page mentions British
  Columbia.
- Conflicting wording in the Terms of Use (line 190): "We provide this Website for use only by persons located in the
  United States. We make no claims that the Website or any of its content is accessible or appropriate outside of the
  United States. ... If you access the Website from outside the United States, you do so on your own initiative and are
  responsible for compliance with local laws." The help centre accepts non-US traders (international payout methods).
- Payout methods (sup_payout_methods.html.txt, capture 2026-10-20, updated 2026-08-26): "Plaid / Instant bank
  transfers for U.S.-based traders"; "WorkMarket by ADP / Available for both U.S. and international traders / Can
  withdraw via bank transfer or Paypal / Funds can typically be received as early as the next business day"; "Crypto /
  Available for International Traders" (BTC, ETH, LTC, USDT, USDC). A BC resident would use WorkMarket or crypto.
- Currency: not stated (amounts are in USD; the CAD conversion route is unknown).
- KYC: general FAQ: "Do you require KYC, and when? Yes — at the time of payout when required by the payout provider."
  Business registration: "If you register as a business, payouts must be issued to the business and require business
  verification documents." Tax forms: "For U.S. traders, tax forms (e.g., 1099) may be issued where applicable."
  Nothing Canada-specific.
- Purchases: card payments only (sup_pay_methods: Visa, Mastercard, American Express, Discover, Diners Club, Maestro).

## 8. Search budget and failures

- WebSearch calls used: 11 of 40 (each logged in log.tsv). Firecrawl: 1 call, failed (no credits); Firecrawl gov search: 1 call (free), no hits.
- Failures: today's pricing page returned 403 to WebFetch; the Wayback copies of refund-liability-policy had no
  snapshot; several Wayback fetches timed out and were retried (log shows only successful lines plus failures noted).
- Unknowns: today's (2026-10-21) price; whether commissions include exchange and NFA fees; which API is allowed and any
  rate limit; VPS policy; sim fill rule; currency for Canadian payouts; NFA BASIC record.
