# A2 firm facts: Tradeify (tradeify.co, help.tradeify.co), as of 2026-10-21

Worker: A2_tradeify (Stage E.28 Part A, Layer 2 facts; no scoring). Started 2026-10-21 05:43 PDT.
Pages: reports/stage_e28_briefs/pages/A2_tradeify/ (log.tsv, DO_NOT_COMMIT.txt). Scratch: work/A2_tradeify/.
Machine-readable copy: A2_firm_tradeify.json (fields {"value","unit","source_file","quote","note"}).

## 0. Access route and evidence quality (read first)

- Terms check. tradeify.co/terms-of-use (E.25 copy, curl 2026-10-18T08:40:34Z, sha256 1d321f74...,
  stage_e25_briefs/pages/R9/terms_tradeify.html, line 56 of the text extract) forbids it: "use any robot, spider,
  scraper or other automatic device, manual process or application or data mining, scraping or extraction tool to
  access, harvest, monitor, copy or use the Site without the express written permission of Tradeify". Decision
  (logged): no Scrapling and no curl on tradeify.co or help.tradeify.co.
- Routes used: (a) Wayback copies (curl of web.archive.org), raw HTML saved, files `tf_*_wb.html` (+ `.txt`,
  `.body.txt` extracts); (b) E.13 copies of help pages (stage_e13_briefs/pages/PropVenues1/tf_*.txt, fetched
  2026-10-03), used as pointers and as the dated earlier version; (c) **deviation fetches**: one WebFetch per page,
  2026-10-21. help.tradeify.co answers WebFetch with HTTP 403, so the deviation fetches went to the Intercom
  mirror of the same help centre, intercom.help/tradeify/... (same content and owner; treated as covered by the same
  terms). The WebFetch tool returns a model's extraction, not raw HTML: it declined full verbatim copies, but
  returned quoted sentences and table cells. Those are saved as `tf_wf_*.txt` and listed in DO_NOT_COMMIT.txt.
  Wherever a raw copy (Wayback or E.13) has the same sentence, the raw copy is the quote source and the deviation
  fetch is the "still true today" check.
- Every help article fetched today showed "Updated this week" or "Updated yesterday": Tradeify edited its help
  centre during 2026-10-14..10-21. Several facts changed between the 2026-10-03 E.13 copies and today (listed in 6.4).
- Tradeify's marketing homepage (Wayback capture 2026-10-19, tf_home_wb.html) renders its plan cards by
  JavaScript; the static HTML carries template placeholders ("Lorem ipsum dolor.", the same "$359 / $251" on every
  card), so no price or rule is taken from it. Its plan tab order is: "Growth | Pass in 1 day", "Select | Pass in 3
  days", "Lightning | Instant".

## 1. Standard 50K plan and its funded stage

### 1.1 Which plan is "the standard 50K plan" under the spec rule

The spec (section 3) takes "the first 50K evaluation plan on its pricing page on the lookup date". Tradeify sells
three plan families in 25K/50K/100K/150K: Growth (evaluation), Select (evaluation) and Lightning (instant funding,
no evaluation). On the homepage tab order and in the help-centre Pricing Reference, Growth comes first
(tf_home_wb.html.txt lines 125-131; tf_wf_pricing.txt "Growth 50K | $145 | $95" is the first 50K row). So the
first 50K evaluation plan is **Growth 50K**. Select 50K facts are given in 1.4 in case the lead reads the rule
differently (the selection is the lead's).

### 1.2 Growth 50K evaluation

| Fact | Value | Source file | Verbatim quote |
|---|---|---|---|
| Price | USD 145, list | tf_wf_pricing.txt (today, "Updated yesterday"); same in E.13 tf_pricing.txt (2026-10-03) | "Growth 50K \| $145 \| $95" |
| Billing | one-time, no subscription | tf_wf_pricing.txt; tf_growth_eval_wb.html.body.txt (Wayback 2026-10-14) | "All plans are one-time purchases with no recurring billing." / "GROWTH™ evaluation accounts are a one-time purchase. There are no recurring subscription charges." |
| Reset fee | USD 95 | tf_wf_pricing.txt | "Growth 50K \| $145 \| $95" |
| Discounts | promo codes recur (homepage banner "Get funded - 35% OFF", code fields); 5-account bundle 5% off | tf_home_wb.html.txt line 117-121; E.13 tf_pricing.txt | "Tradeify offers a 5-account bundle discount on Growth 25K, Growth 50K, Select 25K, and Select 50K Evaluations" |
| Profit target | USD 3,000 | tf_growth_eval_wb.html.body.txt (raw, lastUpdated 2026-10-14); tf_wf_growth_eval.txt (today) | table row "$50k \| $3,000 \| $1,250 \| $2,000 \| 4 Contracts (40 Micros)" |
| Max loss type and amount | end-of-day trailing, USD 2,000; updates at EOD, enforced in real time on net liquidation value; no lock in evaluation | tf_growth_eval_wb.html.body.txt; E.13 tf_drawdown.txt | "The GROWTH™ evaluation uses an End of Day Trailing Max Drawdown, which is based on the account balance at the end of the trading day." / "The level is still enforced in real time: if your net liquidation value touches it at any moment, the account fails immediately" / "Q: Does drawdown lock on Evaluation accounts? A: No." |
| Daily loss limit | USD 1,250, soft breach (trading stops for the day, account not failed) | tf_growth_eval_wb.html.body.txt; tf_wf_essential.txt | "GROWTH™ evaluation DOES have a Daily Loss Limit (soft breach): $600 (25K), $1,250 (50K) ... If you hit it, trading stops for the day but your account is not failed." |
| Consistency rule | none in the evaluation (changed: E.13 copy of 2026-10-03 said 35%) | tf_growth_eval_wb.html.body.txt; tf_wf_pricing.txt | "A: No. GROWTH™ evaluation does NOT have a consistency requirement." / "No consistency rule during the evaluation (35% on funded payouts)." |
| Minimum days | 1 | tf_growth_eval_wb.html.body.txt | "Minimum Trading Days \| 1 day (can pass immediately)" |
| Time limit | none; weekly activity rule (>= 1 trade per Mon-Fri week per account) | tf_growth_eval_wb.html.body.txt; tf_wf_guidelines.txt | "Q: Is there a time limit to complete GROWTH™ evaluation? A: No. There is no deadline to hit the profit target" / "you must place at least one trade per week (Monday through Friday)" |
| Activation fee | none; activation instant | tf_growth_eval_wb.html.body.txt; tf_wf_pricing.txt; tf_getfunded_wb.html.body.txt | "There is no time activation fee." / "There are no activation fees for any current Tradeify account type." |
| Funded start balance | base size (USD 50,000); evaluation profits do not carry | tf_getfunded_wb.html.body.txt (Wayback 2026-06-24) | "Your funded account starts at your base account size ($50K, $100K, or $150K) regardless of your evaluation ending balance." |
| Activation cap | max 5 Growth funded activations per day; max 5 sim funded active | tf_growth_eval_wb.html.body.txt | "You can activate a maximum of 5 GROWTH™ Funded accounts per day. ... You cannot have more than 5 sim funded accounts active at any time." |
| Position limit | 4 minis or 40 micros, combined at 10:1 (5/50 for accounts bought before 2025-09-12) | tf_growth_eval_wb.html.body.txt; tf_wf_essential.txt | "4 Contracts (40 Micros)" / "10 Micro contracts = 1 Mini contract" |
| Microscalping rule | not in the evaluation (guidelines page); but see the conflict note in 4 | tf_wf_guidelines.txt | "This rule applies to funded accounts only." "It does not apply during an evaluation." |
| Monthly cap on evaluations | 15 per month (mentioned in passing) | E.13 tf_pricing.txt (2026-10-03) | "it does not count toward the 15-evaluation monthly limit" |

### 1.3 Growth 50K sim funded stage

| Fact | Value | Source file | Verbatim quote |
|---|---|---|---|
| Sim or live | simulated ("Sim Funded"); Tradeify may move a trader to a Live Funded (Elite Live) account after any successful payout | tf_growth_payout_wb.html.body.txt (Wayback 2026-10-11, lastUpdated 2026-09-10); tf_wf_growth_payout.txt (today) | "Tradeify reserves the right to move you to a Live Funded Account at any time after a successful payout." |
| Max loss | EOD trailing USD 2,000 from USD 50,000; locks when EOD balance reaches USD 52,100 (or at the first payout request), floor then fixed at USD 50,100 | E.13 tf_drawdown.txt (2026-10-03, dateModified 2026-08-26) | "On Sim Funded accounts (not Evaluations), your drawdown locks in place once you profit beyond the drawdown amount by $100, or immediately when you request a payout - whichever comes first." / "A 50K Growth account with $2,000 drawdown locks when EOD balance reaches $52,100. The drawdown floor becomes $50,100 and never moves up again." |
| Daily loss limit | USD 1,250 (soft breach) | tf_wf_essential.txt (today) | "Growth Accounts: Daily loss limit varies by account size ($1,250 for $50k, $2,500 for $100k, $3,750 for $150k)" |
| Reset | funded account cannot be reset | tf_growth_eval_wb.html.body.txt | "the Simulated Funded counterpart cannot be reset." |
| Split | 90% to trader (sim funded); 80% on Elite Live | tf_growth_payout_wb.html.body.txt; tf_wf_pricing.txt | "Traders receive 90% of the payout amount requested." / "Elite Live accounts: 80% to trader / 20% to Tradeify" |
| Balance needed to request | USD 53,000 (accounts bought from 2025-09-12) | tf_growth_payout_wb.html.body.txt; tf_wf_growth_payout.txt | "$50,000 \| $53,000" / "your balance must reach at least ... $53,000 on a $50,000 account" |
| Buffer after payout | balance must stay above the locked floor USD 50,100 | tf_growth_payout_wb.html.body.txt | "your balance cannot go below $50,100 without "failing" the account. You ARE able to take out that amount, but you would leave yourself with $1,400 in drawdown room." |
| Payout cap per request | 1st USD 1,500; 2nd 2,000; 3rd 2,500; 4th and later 3,000 (hard cap; remainder stays in account) | tf_growth_payout_wb.html.body.txt; tf_wf_growth_payout.txt | table rows "1 \| $1,000 \| $1,500 ...", "2 ... $2,000", "3 ... $2,500", "4+ ... $3,000"; "These are hard caps" |
| Minimum payout | USD 500 | tf_growth_payout_wb.html.body.txt | "$500 for $50k accounts" |
| Winning days per payout | 5 days each with profit > USD 150; count resets after each payout | tf_growth_payout_wb.html.body.txt | "Minimum Trading Days: 5 or more of the Trading Days must show a profit greater than: ... $150 in profit for 50k accounts" / "The Trading Day count resets to zero after each successful payout." |
| Consistency (funded) | 35% | tf_growth_payout_wb.html.body.txt; tf_wf_essential.txt | "Consistency Rule: Abide by the 35% Consistency Rule" / "Growth Funded: 35% limit" |
| Microscalping (payout gate) | > 50% of trades and > 50% of profit from trades held > 10 s; failing it blocks payout, does not fail account | tf_guidelines_wb.html.body.txt (Wayback 2026-08-22); tf_wf_guidelines.txt (today) | "Over 50% of your trades are longer than 10 seconds" / "Over 50% of your profit must come from trades held longer than 10 seconds." |
| Frequency | no fixed calendar; once conditions met (in practice every >= 5 qualifying days); one open request at a time | tf_growth_payout_wb.html.body.txt; tf_wf_essential.txt | "Payout requests can be submitted directly from your dashboard once payout conditions have been met." / "you cannot submit another payout request on that account until it has been processed" |
| Processing time | issued 24-48 h after approval; up to 72 h outside business hours | tf_growth_payout_wb.html.body.txt (raw, 2026-10-11). Today's WebFetch said "within 24 hours"; not confirmed verbatim, treat 24-48 h as the quote | "Payments will be issued within 24-48 hours after the withdrawal has been processed." |
| Scaling plan | none for Growth: full size from day one (Select funded scales) | tf_wf_essential.txt | "Growth and Lightning use their maximum position size from day one; Select funded accounts scale up as the account grows" |
| Max accounts | 5 sim funded (any mix of Growth, Select, Lightning), per household | tf_growth_payout_wb.html.body.txt; tf_wf_pricing.txt | "Traders can have a maximum of 5 total Simulated Funded Accounts" / "The 5-account cap applies to active Sim Funded accounts per household." |
| Daily reconciliation | 18:00-20:00 ET | tf_growth_payout_wb.html.body.txt | "Daily account reconciliations occur between 6:00 p.m. and 8:00 p.m. EST/EDT." |
| Live stage | Elite Live: 80/20 split plus a "Performance Reward Pool" (USD 4,000 for 50K; monthly reward up to USD 2,000 with 5 days >= USD 250 and month profit > USD 2,000); 3.0% of funded traders were called up to live in Aug 2025 - Jul 2026 (firm statistic) | tf_30_wb.html.body.txt (Wayback 2026-07-13, lastUpdated 2026-04-07); tf_home_wb.html.txt line 458 | "$50K \| $4,000"; "Achieve 5 profitable days ($250 or more per day)"; "(d) 3.0% of individual participants trading in a Funded Account were called up to a Live Funded Account." |

Simulator mapping notes (for EconCoder; facts only, the mapping choices are the lead's):
- Evaluation: start 50,000; pass when balance >= 53,000 (target 3,000) with no consistency check and no minimum
  beyond 1 day; fail when intraday net liquidation <= (max EOD balance so far - 2,000), floor never lowers and
  never locks in the evaluation; daily loss of 1,250 stops the day without failing. Fee 145 per attempt, 95 per reset
  (resets are optional; a fresh purchase is 145).
- Funded: restart at 50,000 with an EOD trailing 2,000 floor that locks at 50,100 once EOD balance >= 52,100 or at the
  first payout request; DLL 1,250 soft. A payout request needs balance >= 53,000, 5 days each > 150 profit since
  the last payout, the 35% consistency rule (largest day / total profit, per the Consistency Rule article, not
  fetched today: [unverified wording]), and the 10-second hold rule. Withdraw min(cap_k, available), with
  cap_1..4+ = 1,500 / 2,000 / 2,500 / 3,000, minimum 500; trader receives 90%. The account stays live after a payout;
  no funded reset.
- Firm statistics (claims): 17.2% of evaluation accounts passed; 28.5% of funded participants received a payout
  (Aug 2025 - Jul 2026, tf_home_wb.html.txt line 458).

### 1.4 Select 50K (alternative reading of the spec rule; not the first-listed plan)

| Fact | Value | Source | Quote |
|---|---|---|---|
| Price / reset | USD 165 / 109 (40% consistency); USD 205 / 135 with the 50% add-on | tf_wf_pricing.txt | "Select 50K \| $165 \| $109"; "Select 50K \| $205 \| $135" |
| Evaluation | target USD 3,000 (raised from 2,500 in Tradeify 3.0), no DLL, 40% consistency, min 3 days | tf_30_wb.html.body.txt; tf_selvsgrowth_wb.html.body.txt; tf_wf_pricing.txt | "Select 50K Profit Target Increased from $2,500 to $3,000"; "No DLL during evaluation." |
| Funded paths | Select Daily (DLL USD 1,000 at 50K, daily payouts) or Select Flex (no DLL, 5 winning days per payout); funded size scales with account growth | E.13 tf_essential.txt (2026-10-03); tf_wf_essential.txt | "Select Daily: Daily loss limit varies by account size ($1,000 for $50k ...)"; "Select Flex: 5 winning trading days required per payout cycle" |
| Drawdown | EOD trailing, lock at USD 52,100 to floor 50,100 (same mechanism) | E.13 tf_drawdown.txt | "a 50K Select account locks when EOD balance reaches $52,100, and the drawdown floor becomes $50,100 permanently." |

Select payout caps and buffers were not fetched (Select Flex and Select Daily Payout Policies article): open item.

## 2. Products, fees and position limits

Sources: product list, tf_wf_products.txt (today, "Updated this week") and its raw Wayback copy tf_products_wb.html
(capture 2026-07-09, article dated 2026-05-20; tables extracted to tf_products_wb.tables.txt), with the rule "only
products listed in the tables above are supported" (raw: "Never assume a micro version of a standard contract exists
— only products listed in the tables above are supported."). Fees: tf_wf_comm.txt (today, "Updated this week") and
raw Wayback copy tf_comm_wb.html (capture 2026-07-09, lastUpdated 2026-04-28). The fee page states: "Total Round
Trip Cost includes Exchange fees, NFA fees, Clearing fees, and Commissions." / "All costs are per contract round trip
(both sides of the trade)" / "(All fees are based on the free membership structure.) All prices PER contract."
Tradeify quotes round trips only; the per-side figure below is RT / 2 (derived, not quoted). The pricing reference
says broker choice adds no surcharge (tf_wf_pricing.txt: "Rithmic: No additional platform fee. Same pricing as
Tradovate and other platforms."); the fee page itself does not mention brokers. The product list does not vary by
plan: it is firm-wide, so the Growth 50K (and Select 50K) plan has the same list.

| Code | Allowed | RT USD (today) | Per side USD (derived) | Earlier raw value (date) | Note |
|---|---|---|---|---|---|
| MNG | no (not listed) | - | - | - | no micro natural gas in the tables |
| QG | yes | 4.00 | 2.00 | 4.00 (2026-07-09) | "E-Mini Natural Gas \| QG \| NYMEX \| $4.00" |
| NG | yes | 6.20 | 3.10 | 6.20 | |
| MCL | yes | 2.12 | 1.06 | 2.12 | CME raised MCL exchange fee on 2026-10-01 (Topstep snippet [snippet]); Tradeify's figure unchanged |
| QM | yes | 5.40 | 2.70 | 5.40 | |
| CL | yes | 5.98 | 2.99 | 6.00 (2026-07-09); 5.66 in pricing reference (2026-10-03) | changed this year; today both pages say 5.98 |
| MGC | yes | 2.12 | 1.06 | 2.12 | "The only micro metal Tradeify supports is MGC." |
| GC | yes | 6.20 | 3.10 | 6.20 | |
| SIL | no (explicitly) | - | - | - | "The CME 1,000 oz Micro Silver (SIL) is not a Tradeify-supported product." |
| SI | yes | 6.20 | 3.10 | 6.20 | full-size 5,000 oz |
| MHG | no (not listed) | - | - | - | "The only micro metal Tradeify supports is MGC." |
| HG | yes | 6.20 | 3.10 | 6.20 | |
| M6E | yes | 1.60 | 0.80 | 1.60 | |
| 6E | yes | 6.20 | 3.10 | 6.20 | |
| M6A | yes | 1.60 | 0.80 | 1.60 | |
| 6A | yes | 6.20 | 3.10 | 6.20 | |
| MET | no (explicitly: crypto) | - | - | - | "Tradeify does not support any cryptocurrency derivatives, including Bitcoin futures." |
| ETH | no (explicitly: crypto) | - | - | - | same |
| MBT | no (explicitly: crypto) | - | - | - | same |
| BTC | no (explicitly: crypto) | - | - | - | same |
| M2K | yes | 1.82 | 0.91 | 1.82 | |
| RTY | yes | 5.76 | 2.88 | 5.76 | |
| MYM | yes | 1.82 | 0.91 | 1.82 | |
| YM | yes | 5.76 | 2.88 | 5.76 | |
| MNQ | yes | 1.82 | 0.91 | 1.82 | |
| NQ | yes | 5.76 | 2.88 | 5.76 | |
| 2YY, 5YY, 10Y, 30Y | no (not listed) | - | - | - | no US rates table; only EUREX bond futures (Tradovate only) |
| ZT, ZF, ZN, ZB | no (not listed) | - | - | - | same; WebSearch found no Tradeify statement either way |
| micro grains (MZC, MZS, MZW, MZL, MZM) | no (not listed) | - | - | - | agricultural table lists full-size only |
| XC, XK, XW | no (not listed) | - | - | - | |
| ZC | yes | 7.20 | 3.60 | 7.20 | |
| ZS | yes | 15.20 | 7.60 | 15.20 | |
| ZW | yes | 17.20 | 8.60 | 17.20 | |
| ZL | yes | 7.20 | 3.60 | 7.20 | |
| ZM | yes | 9.20 | 4.60 | 9.20 | |

Others listed but outside the candidate set: ES, MES (1.82), EMD, NKD (no fee listed), 6B, 6J, 6C, 6S, HE, LE, GF, QO,
PL, PA (no fee listed), and EUREX index and bond futures (EUR fees, "Tradovate only", extra exchange subscription).
The July raw copy also listed "E-Mini Silver | QI | COMEX | $5.00" in the fee table; today's fee table has no QI row.

Position limits at 50K (Growth evaluation and Growth funded): 4 minis or 40 micros; minis and micros may be held
together, counted at 10 micros = 1 mini (tf_wf_essential.txt: "10 Micro contracts = 1 Mini contract"; E.13
tf_essential.txt: "You can hold minis and micros at the same time. Your combined position must stay within your
account's contract limit, counted at this 10:1 ratio."). The limit is the same for every product (no
product-specific limit table was found). Accounts bought before 2025-09-12 08:00 ET: 5 minis / 50 micros. Fee note
from the firm: "If you're trading micro contracts in multiples of 10, you should trade the corresponding mini
contract instead to save on fees." (tf_comm_wb.html.body.txt).

## 3. Product restrictions, news, hours and flat-by times

- News: no restriction on any product or account. Raw (tf_news_wb.html.body.txt, Wayback 2026-06-24, article
  lastUpdated 2026-04-02): "We do not have any rules against or guidelines around trading news events." / "You trade
  news AT YOUR OWN RISK." Today (tf_wf_essential.txt): "Restrictions: None - news trading is allowed on all
  accounts"; and the guidelines page (tf_wf_guidelines.txt, matching raw tf_guidelines_wb.html of 2026-08-22): "We do
  not have any rules against or guidelines around trading news events," "Dollar Cost Averaging (DCA), flipping, or
  scaling."
- Product-specific restrictions: none found beyond the product list itself (no EIA, auction or contract-specific
  windows on any page read). EUREX products are "Tradovate only". Hedging rule (firm-wide): no opposing positions on
  the same instrument or two products in the same Product Group, in one account or across accounts
  (tf_guidelines_wb.html.body.txt: "You cannot hold opposing positions — one long, one short — on the same
  instrument or on two products from the same Product Group, whether those positions sit in a single account or are
  spread across several of your accounts."). The Product Groups table (Rules: Hedging & Correlated Products,
  10495868) was not fetched.
- Hours: CME Globex hours, 18:00 ET Sunday-Thursday open to 17:00 ET close; trading day 18:00-17:00 ET
  (tf_wf_essential.txt: "Market Open: 6:00 PM Eastern Time (Sunday to Thursday evenings)" / "A trading day runs from
  6:00 PM ET to 5:00 PM ET the next calendar day.").
- Flat-by: 16:45 ET every trading day (13:45 PT), 12:59 ET on holiday early-close days; no overnight carry across the
  daily break, no weekend holds; positions left open are closed by the firm, without failing the account
  (tf_wf_essential.txt: "Close all positions by 4:45 PM Eastern Time (Monday-Friday)" / "Close all positions by
  12:59 PM Eastern Time"; E.13 tf_times_f.txt (2026-10-03, dateModified 2026-07-14): "If you have open positions
  when the market closes, Tradeify will automatically close them for you. This automatic closure will NOT result in
  account failure or loss of your account."). Holding through the overnight session within one trading day is
  allowed (E.13 tf_times_f.txt: "A Tradeify trading session runs from 6:00 PM ET to 4:45 PM ET the next calendar day
  - that's nearly 23 hours."). The excluded window per day is 16:45-18:00 ET (75 of 1,440 minutes incl. the CME
  60-minute break), for every product.
- Live accounts: the same flat-by rule (E.13 tf_times_f.txt: "The no overnight positions rule applies to ALL
  Tradeify account types, including Live accounts.").

## 4. Automation, APIs and order-rate / hold rules

| Fact | Value | Source file | Verbatim quote |
|---|---|---|---|
| Bots / algorithms | allowed "under certain conditions": sole ownership provable, not shared with other traders or firms, not used across multiple firms, not HFT; firm may require a live video of the trader enabling the code on their own PC. The page does not limit this to one stage (applies to evaluation and funded). | tf_guidelines_wb.html.body.txt (Wayback 2026-08-22, lastUpdated 2026-08-12); today tf_wf_guidelines.txt, same text | "At Tradeify, we allow the use of bots and algorithms under certain conditions:" / "We will also require a live video of you enabling the code on your own PC." / "Personal bots are allowed as long as they are not high-frequency trading (HFT) bots." |
| API access | **The Tradovate API is not available on evaluation or sim funded accounts; only on LIVE funded accounts.** No statement found on Rithmic R|API / R|Protocol. ProjectX/TopstepX is not a Tradeify platform. So in the evaluation and sim funded stages automation runs only inside a desktop/web platform (NinjaTrader via Tradovate credentials; Quantower, Sierra Chart, R\|Trader via Rithmic; TradingView via Tradovate, where third-party webhook bridges exist [snippet, vendor pages, pointer only]). | tf_products_wb.tables.txt (raw, Wayback 2026-07-09); tf_wf_products.txt (today) | "Q: Can I use the Tradovate API? A: The Tradovate API is only available for LIVE funded accounts. It is not available for evaluation or sim funded accounts." |
| Risk & Compliance FAQ | automation "only as expressly allowed"; prohibits "prohibited high-frequency systems", "unauthorized or unowned bots/strategies", "prohibited trade-copying", "synchronized trading" | tf_wf_riskfaq.txt (deviation fetch; no Wayback capture) | "Automated trading is permitted only as expressly allowed, and traders remain fully responsible for its activity." / "No trading technology exempts a trader from any Tradeify rule." |
| HFT definition / order-rate limit | none published (HFT banned without a numeric threshold; "risk measures" undisclosed) | tf_guidelines_wb.html.body.txt; tf_wf_riskfaq.txt; E.25 terms copy | "Tradeify has specific risk measures in place to detect and monitor such activities." / terms: "Tradeify is not obligated to disclose the specific methods, technologies, indicators, thresholds, or information used to identify prohibited activity" |
| Minimum hold / microscalping | funded payout gate: > 50% of trades AND > 50% of profit from trades held > 10 s; blocks payout, does not fail the account; guidelines: funded only, not evaluations. Conflict: the News Trading article (raw Wayback 2026-06-24, lastUpdated 2026-04-02) says failing it also blocks "activate the evaluation". A 1-minute-hold strategy meets either reading. | tf_guidelines_wb.html.body.txt; tf_wf_guidelines.txt; tf_news_wb.html.body.txt | "This rule applies to funded accounts only. It does not apply during an evaluation." / news page: "If you do not meet the criteria, you will not be able to activate the evaluation or request a payout." |
| Scalping as such | no rule beyond the 10-second gate; flipping, scaling and DCA permitted | tf_guidelines_wb.html.body.txt | "We do not have any rules against or guidelines around trading news events, Dollar Cost Averaging (DCA), flipping, or scaling." |
| Exploiting sim fills / platform errors | prohibited: errors, price-display discrepancies, update delays; "exploitation of simulated conditions" listed as prohibited | tf_guidelines_wb.html.body.txt; tf_wf_riskfaq.txt | "traders are prohibited from using strategies that seek to exploit or create errors within our platform. This includes taking advantage of discrepancies in price displays, delays in updates, or any other technical errors in our services." / "A platform's technical permissiveness does not make an action compliant." |
| Other prohibited | hedging (same instrument or same Product Group, within or across accounts); copy trading between different traders; multi-firm use of the same bot | tf_guidelines_wb.html.body.txt; tf_wf_riskfaq.txt | "Hedging is prohibited." |
| Activity minimum | >= 1 trade per Mon-Fri week per account (evaluation and funded) | tf_guidelines_wb.html.body.txt | "To keep your funded or evaluation account active, you must place at least one trade per week (Monday through Friday). This is per account, not per user." |

## 5. Platforms, simulated fills, VPS

- Brokers/platforms (chosen at checkout, cannot switch broker later): Tradovate (Tradovate web/desktop, NinjaTrader,
  TradingView), Rithmic (Tradesea, Quantower, Sierra Chart, R|Trader), WealthCharts (own platform only). Raw:
  tf_platforms_wb.html.body.txt (Wayback 2026-10-13, lastUpdated 2026-08-05): "Tradeify supports three broker
  connections: Tradovate, Rithmic, and WealthCharts. You select your broker at checkout." / "you cannot switch between
  brokers (e.g., from Tradovate to Rithmic) without purchasing a new account." Today: tf_wf_pricing.txt "At checkout,
  you select one of three brokers: Tradovate, Rithmic, or WealthCharts." Rithmic and Tradesea were added in Tradeify
  3.0 (tf_30_wb.html.body.txt: "New supported platforms: Rithmic Tradesea").
- Market data: Level 1 CME included; Level 2 depth only on Tradovate (paid add-on bought from Tradovate); not
  available on Rithmic or WealthCharts (tf_platforms_wb.html.body.txt: "Level 2 (L2) depth of market data and EUREX
  data are available on Tradovate accounts only, purchased directly from Tradovate.").
- Native OCO/bracket orders: not documented on the pages read (the Tradovate, NinjaTrader and Rithmic platforms
  themselves offer them; no Tradeify page fetched states it). [unverified]
- **Simulated fill rule for resting limit orders: not documented by Tradeify** on any page read (products, platforms,
  guidelines, risk FAQ, essential rules, pricing). Two WebSearches (Tradeify sim fills; Tradovate simulation limit
  fills) found no Tradeify or Tradovate official statement; only forum anecdotes (Tradovate community 2021: limit
  orders filled only when price "breaking through", user claim, pointer only) [snippet]. The evaluation and sim
  funded accounts run on Tradovate's or Rithmic's simulation engine depending on the broker chosen.
- VPS: conditionally prohibited. Terms of use (E.25 copy 2026-10-18 and E.13 copy 2026-10-03, line 57-58 of the E.13
  text): "use a Virtual Private Server (“VPS”), virtual machine, virtualized environment, remote computing
  environment, or similar technology to access or use Tradeify’s Site, platform, accounts, or services where such
  technology obscures, alters, masks, or prevents Tradeify from reliably verifying the user’s device, network,
  location, identity, or account activity". Risk FAQ (tf_wf_riskfaq.txt): review may follow access "through
  prohibited virtualization, remote-access, anonymization, or circumvention technologies." The bot rule's "live
  video of you enabling the code on your own PC" also points to the trader's own machine. A third-party blog says
  Tradeify bans login via VPN or VPS and calls VPS use "own risk" after a normal login (proptradingvibes.com, German,
  "Stand August 2026") [snippet, pointer only]. No first-party page permits a Chicago VPS explicitly.
- API rate limit: none published by Tradeify (and the Tradovate API is unavailable before Live, see 4).

## 6. Reliability

### 6.1 Founding and scale
- Operating since at least December 2022 under the name: Wayback capture 2022-12-05 of tradeify.co
  (tf_home_2022_wb.html.txt): "Tradeify – Accessible trading education and funding" / "Learn how to trade without
  risk, prove you can succeed and get a funded $50,000 trading account. No catch." / "2 weeks for free, and only
  $99/mo afterwards." The Wayback banner shows "353 captures 26 Dec 2021 - 19 Oct 2026" (the 2021 capture is a 301
  redirect). A Finance Magnates interview (E.25 file stage_e25_briefs/pages/R8/fm_tradeify_founders.txt, line 110)
  says the futures prop firm was co-founded "in 2024" by Brett Simberkoff and Vinan Mistry (interview: pointer only).
  Either way the firm has operated for more than 2 years before 2026-10-21.
- Entity: the terms name Florida law ("The laws of the State of Florida will govern these Terms of Use", E.25 terms
  copy) and an affiliated introducing broker, "Tradeify Brokerage LLC d/b/a Slay Markets is an introducing broker
  registered with the Commodity Futures Trading Commission ("CFTC") ... and is a NFA Member (NFA ID: 0575972)" (E.25 terms copy as text in work/A2_tradeify/tf_terms_e25.txt;
  terms copy, text line 141). NFA BASIC could not be read: the profile page is a JavaScript shell, its data endpoint
  answered HTTP 403 to curl, and no browser was available (Playwright: Chrome not installed). Registration status
  and the NFA/CFTC action record for ID 0575972 are therefore **[unverified]** (firm self-statement only).

### 6.2 Payout track record and speed (the firm's claims, as claims)
- "Over $350 million in verified payouts" and "1 hour payouts" (homepage, tf_home_wb.html.txt, Wayback 2026-10-19;
  "Request a payout, get paid in minutes. Daily payouts available on Select plans.").
- Help centre: "Payments will be issued within 24-48 hours after the withdrawal has been processed." and up to 72 h
  outside business hours (tf_growth_payout_wb.html.body.txt, 2026-10-11). Rise withdrawal: "Bank: 1-3 days, Crypto:
  Usually within hours." (tf_rise_wb.html.body.txt, Wayback 2026-06-10).
- Firm statistics, Aug 2025 - Jul 2026 (homepage disclosure, tf_home_wb.html.txt line 458): "(a) 17.2% of evaluation
  accounts initiated were successfully completed ... (c) 28.5% of individual participants at the Funded Level
  received a payout; and (d) 3.0% of individual participants trading in a Funded Account were called up to a Live
  Funded Account."

### 6.3 Disputes and regulatory actions
- Regulatory actions against the firm: **none found**. Firecrawl government-index search (CFTC, FTC, NFA, state AG
  terms with "Tradeify") returned only generic CFTC enforcement index pages, none naming Tradeify; WebSearch
  ("Tradeify lawsuit OR attorney general OR CFTC OR FTC") found no court filing, order or agency release; BCSC
  Investment Caution List search found no Tradeify entry. Absence in search is a gap, not proof; NFA BASIC unread.
- Payout disputes in the past 12 months: only from review sites and Trustpilot summaries, which are pointers, not
  evidence: thetrustedprop.com "Tradeify Reported Payout Denials 2026" (search summary: "at least 10 one-star
  Trustpilot reviews dated September 15 to October 4, 2026 allege payouts withheld or accounts closed after a
  compliance review"); a PropFirmMatch reviewer says they filed an FTC consumer report (a report, not an agency
  finding) [snippet]. Tradeify publishing a new "Risk & Compliance Guidelines: FAQ" and a "Know Your Trader (KYT)
  Policy" (Business & Compliance collection, Wayback 2026-10-03: articles 17069653 and 17229690) is consistent with
  more account reviews, but that is an inference, not a fact. Whether these count as "documented" for Rel is the
  lead's call.

### 6.4 Rule changes in the 12 months to 2026-10-21 (dated where possible)
| When | Change | Direction for a trader | Source |
|---|---|---|---|
| 2026-03 to 04 (Tradeify 3.0, article lastUpdated 2026-04-07) | subscriptions ended, one-time fees only, "Up to ~3% price increase across Select and Growth plans"; Select 50K target 2,500 -> 3,000; Lightning 150K MLL 5,250 / DLL 3,000; Elite Live reward pool; Rithmic and Tradesea added; instant activation | mixed (price up, target up; no recurring fee) | tf_30_wb.html.body.txt |
| between 2026-04-28 and 2026-10-21 | CL round trip 6.00 -> 5.98 (pricing reference said 5.66 on 2026-10-03); E-mini Silver QI row removed from fee table | minor | tf_comm_wb.html.body.txt; tf_wf_comm.txt; E.13 tf_pricing.txt |
| between 2026-10-03 and 2026-10-14 | Growth evaluation consistency rule removed (E.13 copy: "Growth Evaluation — ... 35% consistency rule"; now none, 35% kept on funded payouts) | favourable | E.13 tf_pricing.txt; tf_growth_eval_wb.html.body.txt; tf_wf_pricing.txt |
| between 2026-10-03 and 2026-10-20 | Growth 100K reset 155 -> 169; Growth 150K reset 215 -> 229 (50K unchanged at 95) | adverse (not at 50K) | E.13 tf_pricing.txt; tf_wf_pricing.txt |
| between 2026-10-03 and 2026-10-21 | Select 300K price 449 -> 349 ("V2; V1 was $449") | favourable (not at 50K) | same |
| by 2026-10 (date unknown) | terms of use carry a VPS / virtual-machine clause and anti-circumvention clause; Risk & Compliance FAQ published (~2026-09) | adverse for a hosted bot | E.13 tf_terms.txt (2026-10-03); tf_wf_riskfaq.txt |
| 2025-09-12 (just outside the 12-month window) | 50K position limit 5 -> 4 minis; payout tiers and minimum payout balance changed (52,100 -> 53,000) | adverse | tf_growth_eval_wb.html.body.txt; tf_growth_payout_wb.html.body.txt |

The help centre was being edited during the lookup week (every page "Updated this week"), so the facts above are as
of 2026-10-21 and may move.

## 7. Eligibility: British Columbia and Canada

- Canada is not on the restricted-country list (58 names; the page's intro says 65) and no province is named.
  Today (tf_wf_restricted.txt): "The page does not mention Canada, British Columbia, Quebec, Ontario, or any US
  state." E.13 raw copy (2026-10-03, tf_restricted.txt): "Full alphabetical list (58 countries): Afghanistan, Albania,
  ..." with no Canada. Residency, not location, governs: "These restrictions apply to your country of residency".
  So BC residents are accepted by omission (no explicit statement that Canada or BC is accepted).
- Canada-specific payout terms: **none found**. Payouts go through Rise (default) or Plane (fallback); KYC by Sumsub
  (government ID + liveness selfie) before the first payout, then Rise KYC (ID, proof of address, tax ID for
  non-US: "International: Tax ID (your country's ID number)"); Rise withdrawal options "Bank Transfer (ACH) - 1-3
  business days", "Crypto Tokens - Hours to 1 day", "Local Currencies - Varies by region" (tf_kyc_wb.html.body.txt
  and tf_rise_wb.html.body.txt, Wayback 2026-06-10, lastUpdated 2026-05-11). Account balances and fees are in USD;
  whether Rise pays CAD to a Canadian bank account is not stated on any Tradeify page [unverified].
- Canadian tax treatment: not researched here (one line belongs in the ranking file, per spec).

## 8. Open items and failures

- NFA BASIC record for Tradeify Brokerage LLC (ID 0575972) unread (JS page; data endpoint 403; no browser).
- Select Flex / Select Daily payout policy (12853966), Lightning payout policy, Consistency Rule article (10468320),
  Hedging Product Groups (10495868), Daily Loss Limit article (10468321) not fetched (outside the Growth 50K path or
  covered by other pages).
- Simulated fill rule: undocumented by Tradeify; not found for Tradovate either.
- Rithmic R|API availability on evaluation/sim funded accounts: no statement found either way.
- Wayback: CDX listing offline / 429 at 12:43-12:47 UTC; several captures failed (000) and were retried; captures of
  "permitted times" (2026-08-21) and "restricted countries" (2026-10-12) were Wayback-stored 403 pages, so the E.13
  copies and today's deviation fetch were used.
- Deviation fetches give model-extracted quotes, not raw HTML. One discrepancy seen: today's payout extraction said
  "within 24 hours", the raw 2026-10-11 copy says "within 24-48 hours"; the raw quote is used.
- WebSearch calls used: 21 of 40; Firecrawl gov search: 1.
