# Stage E.28 A2: Layer 2 firm facts, Bulenox (as of 2026-10-21)

Worker ROOT: A2_bulenox. Facts only; no scores (the lead scores against reports/stage_e28_ranking_spec.md section 3).
Fetch log: reports/stage_e28_briefs/pages/A2_bulenox/log.tsv. Machine-readable copy: A2_firm_bulenox.json.

## 0. Sources and the terms decision

- Terms of Use (PDF, "Updated October 2026"; Wayback capture 2026-10-19, byte-identical text to the E.25 copy of
  2026-10-18) forbid "automated use of the system, such as using any data mining, robots or similar data gathering"
  and any "spider, robot (or "bot"), cheat utility, scraper or offline reader that accesses the Sites"
  (blx_terms_wb20261019.txt lines 173, 192-193). Decision (logged before any fetch): no Scrapling, no curl on
  bulenox.com HTML pages.
- Routes used: (a) Wayback captures (raw) of the site's prerendered pages, of its JavaScript bundle (which holds the
  pricing tiers), and of the help-centre and FAQ CMS JSON (bulenox.com/cms/items/help_items, captured 2026-09-28;
  faq_items, captured 2026-10-08), which is the content the help-center and faq SPA pages render; (b) the official
  rate-sheet PDF, downloaded once today (byte-identical to the Wayback 2026-10-10 copy); (c) three single WebFetch
  deviation fetches today (pricing page, help CMS filtered to 9 items, FAQ CMS), which confirm that every number
  used below is unchanged today. WebFetch returns model-extracted text, not raw HTML; the raw quotes below come
  from the Wayback files and the today checks are cited alongside.
- All bulenox.com material (Wayback copies and deviation fetches) is listed in pages/A2_bulenox/DO_NOT_COMMIT.txt.
- Earlier copies: E.13 saved the pricing page on 2026-10-03 (reports/stage_e13_briefs/pages/PropVenues1/blx_pricing.*;
  same sha256 702e31aa... as the Wayback 2026-09-27 and 2026-10-09 prerenders); E.25 saved the Terms PDF on
  2026-10-18.

File-name key (all under reports/stage_e28_briefs/pages/A2_bulenox/):
- PRICE = blx_wb20261009_accounts-pricing_eod (prerender, 2026-10-09) and blx_wb20260928_index.js (tier data);
  today: blx_dev_pricing_webfetch_20261021.txt
- HELP = blx_wb20260928_cms_help_items.json / .txt (help CMS, 48 items, English extracted by my script);
  today: blx_dev_cms_help_webfetch_20261021.txt
- FAQ = blx_wb20261008_cms_faq_items.json / .txt (18 items); today: blx_dev_cms_faq_webfetch_20261021.txt
- RATES = blx_rates_20261021.pdf / .txt (official rate sheet, "Updated Aug/11/2026")
- TERMS = blx_terms_wb20261019.pdf / .txt

## 1. The standard 50K plan and its funded stage

### 1.1 Which plan

The pricing page has three tabs in this order: "Qualification", "Fast Track", "Momentum" (PRICE). The first tab's
50K card is the standard plan: the Qualification Account, $50,000. Before purchase the trader picks one of two
risk models, "Option 1 · No scaling / Trailing Drawdown" (listed first) and "Option 2 · Scaling plan · Daily loss
limit / End-of-Day Drawdown"; "This choice is locked for the life of the account." (PRICE). Both options cost the
same. Facts for both are given; the spec rule ("the first 50K evaluation plan on its pricing page") points to
Qualification 50K, and Option 1 is the first-listed risk model (lead's call which option to simulate).

### 1.2 Qualification Account (evaluation), $50,000

| Item | Option 1 (trailing) | Option 2 (EOD) | Source and quote |
|---|---|---|---|
| Price | $175 | $175 | index.js tier: `{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}`; PRICE card "$175 / one-time / Access valid for 30 days"; today confirmed (WebFetch: "Costs $175 one-time, with access valid for 30 days") |
| Billing | one-time, 30-day access, no renewal | same | HELP account-cancellation: "Your account is paid once and expires automatically at the end of its access period — no renewal and no recurring charge." |
| Coupon | code BULENOX, "applies the best available discount" (amount not shown) | same | PRICE |
| Profit target | $3,000 | $3,000 | PRICE "Profit target $3,000" |
| Max loss limit | $2,500 trailing intraday (real time, includes unrealized P&L and commissions) | $2,500 end-of-day (closing balance) | HELP option-1: "The trailing drawdown follows your account’s highest value throughout the trading day, including both realized and unrealized (open) profits. It is calculated in real time and includes commissions."; option-2: "The End-of-Day (EOD) drawdown is updated once per trading day, after the market closes." |
| Daily loss limit | none | $1,100 (soft: trading disabled for the day, not a violation) | PRICE "No daily loss limit"; HELP option-2 table "$50,000", "$1,100" and "If your Daily Loss Limit is reached, trading is disabled for the rest of the trading day. This is not considered a rule violation" |
| Contracts | 7 (minis; 1 mini = 10 micros) | scaling by Cash on Hand: up to $1,500: 2; $1,501-4,000: 4; $4,001+: 7 | PRICE "Contracts 7", "1 mini = 10 micros."; HELP option-2 table "$50,000", "Up to $1,500: 2 • $1,501–4,000: 4 • $4,001+: 7" |
| Consistency rule | none found at this stage | none found | No consistency text in any qualification item of HELP (checked by grep); Momentum's own page says "There is no consistency requirement at this stage" for its qualification. [absence, not a quote] |
| Minimum days | none | none | HELP minimum-trading-days: "There are no minimum trading days required to obtain a Master Account." |
| Time limit | 30 calendar days of access per purchase (reset does not extend it); no maximum trading days within that | same | HELP reset: "A reset does not extend your 30-day access period."; FAQ: "There is no minimum and no maximum number of trading days" |
| Reset | $78, restores starting balance, clears P&L and trading days | same | HELP reset: "A reset costs $78 and returns your balance to its starting value ... Your previous profits, losses and trading days are cleared." |
| Overnight | prohibited; flat by 3:59 PM CT | same | HELP rules: "All positions must be closed by 3:59 PM (CT)." / "Holding positions overnight is strictly prohibited." |
| Pass to Master | review, then email with agreement and activation instructions; not automatic | same | HELP after-you-pass: "Reaching the profit target does not automatically open a Master Account. Your Qualification Account must first be reviewed." |
| Market data | non-professional included; professional $116/month (help connection page says $112 per exchange) | same | PRICE "CME, CBOT, NYMEX and COMEX data is billed at $116/month"; HELP rithmic-connection: "Professional traders are required to pay a monthly exchange data fee of $112 per exchange for CME, CBOT, NYMEX, or COMEX." (inconsistent on the firm's own pages) |

### 1.3 Master Account (the funded stage; simulated)

The Master Account is the stage after Qualification and before the live Funded Account. It is simulated: the
glossary calls only the Funded Account "a real brokerage account funded by Bulenox and traded with real money"
(HELP key-terms), the FAQ describes Fast Track, a Master-level account, as "a simulated funded environment" (FAQ),
and every account connects to "Rithmic Paper Trading" (HELP rithmic-connection). [The word "simulated" is not
applied to the Master Account itself in the text; inference from these three quotes.]

| Item | Value | Source and quote |
|---|---|---|
| Activation fee | $148 one-time, both options; no monthly fee | HELP activation-fee table "$50,000", "$148"; "The same activation fees apply to both Option 1 and Option 2 accounts." Today confirmed. |
| Activation window | link valid 7 days; a "Master Account queue" exists before the link | HELP: "Once an activation link is issued, it remains valid for 7 days." / "It does not apply while the account is still waiting in the Master Account queue." |
| Drawdown | $2,500, same model as chosen in Qualification (Option 1 trailing intraday, Option 2 EOD); initial threshold $47,500; locks permanently at $50,100 once account value reaches $52,600 | HELP master-trading-rules table: "$50,000", "$2,500", "$47,500", "$50,100", "$52,600"; "The drawdown becomes permanently fixed when it reaches  starting balance + $100 ." |
| Daily loss limit | Option 1: none. Option 2: $1,100 soft limit, removed once the drawdown locks | HELP: "The Daily Loss Limit is permanently removed once the EOD Drawdown locks at the starting balance + $100." |
| Contracts | Option 1: 7; Option 2: 2 / 4 / 7 by Cash on Hand (both directions) | HELP master-trading-rules scaling table |
| Hours | session 5:00 PM to 4:00 PM CT; flat by 3:59 PM CT; no overnight | HELP master-trading-rules |
| Breach | account closed; Master reset possible, fee "calculated individually" via support | HELP: "exceeding the drawdown threshold closes the Master Account." / "The reset fee is calculated individually for each account." |
| Payout: trading days | at least 10 individual trading days per payout; the next 10 count only after the previous payout is completed | HELP withdrawal-rules: "complete at least 10 individual trading days;" / "For each subsequent payout, another 10 trading days must be completed after the previous payout period has been completed." |
| Payout: minimum | $1,000 | "The minimum payout amount is $1,000." |
| Payout: maximum | $1,500 for each of the first three payouts at 50K; no cap after the third | table "$50,000", "$1,500"; "After the third payout, there is no maximum payout limit." |
| Payout: buffer | Safety Threshold Reserve $2,600 must remain above the starting balance after a payout; first payout needs balance >= $53,600 | "To request the minimum payout of $1,000, the account balance must be at least $50,000 + $2,600 + $1,000 =  $53,600 ." |
| Payout: consistency | best day <= 40% of Total P&L; cumulative over the whole Master period (does not reset after payouts); for the first payout the reserve is included in the calculation; failing it is not a violation | "Your most profitable trading day must not represent more than 40% of your Total P&L for the applicable payout period." / "The calculation does not reset after a payout" / "For the first payout, the Safety Threshold Reserve is included in the Consistency Rule calculation." |
| Payout: split | 100% of the first $10,000 paid from the profile (per trader, across accounts), then 90% | "You receive 100% of the first $10,000 paid from your profile." / "the trader receives 90% of each additional payout;" |
| Payout: frequency | processed weekly on Wednesdays; request by 11:59 PM CT Friday; days between request and Wednesday do not count toward the next 10 | "Payouts are processed once a week, on Wednesdays." |
| Payout: documents | Withdrawal Information Form, ID, W-8BEN (non-US) signed by hand | "The W-9 or W-8BEN form must be signed by hand. Electronic signatures cannot be accepted." |
| Scaling plan | Option 2 only (contracts by Cash on Hand, see above); Option 1 has full size from day one | PRICE "Full contract size from day one — no scaling steps." |
| Max accounts | up to 5 active Master-level accounts (Master, Fast Track, Momentum Master combined); Qualification unlimited; all can be active at once; one profile and one Rithmic User ID per trader; since Oct 2026 one profile per household | HELP multiple-master-accounts: "A trader may hold up to five active Master-level accounts ... All five can be activated right away — there is no unlocking sequence."; TERMS line 70-75 household clause |

### 1.4 Funded Account (live capital, discretionary)

| Item | Value | Source and quote |
|---|---|---|
| Entry | after 3 successful payouts on a Master account; at Bulenox's discretion; not automatic | HELP moving-to-funded: "After completing three successful payouts on your active Master Accounts, your accounts may be considered for transition to a Funded Account. The transition is completed at Bulenox’s discretion and is not automatic after the third payout." |
| Other Master accounts | additional Master accounts with >= 1 payout may also transition; accounts with 0 payouts do not; pending ones stay frozen while a Funded Account is active | HELP consolidation |
| Balance carried over | none: "Profits, balance, equity or other monetary amounts accumulated in your Master-level Account do not transfer to the Funded Account." | HELP consolidation |
| Drawdown | Initial EOD Drawdown $2,000 for a 50K Master | HELP consolidation table "$50,000", "$2,000"; today confirmed |
| Declining | "If you do not consent to the transition, the applicable Master Account will be closed and no additional Reward will be issued from that account." | HELP moving-to-funded |
| Live rules (DLL, payout split, caps) | not published in the help centre; governed by the Funded Account Agreement (not public) | [not found] |

### 1.5 Simulator mapping notes (facts for EconCoder, not decisions)

- Cycle cost at 50K: $175 per 30-day Qualification purchase, plus $78 per reset within the same 30 days (resets do
  not extend the window), plus $148 activation on passing. No monthly fee at any stage.
- The Qualification has a hard 30-calendar-day clock per purchase; a failed or expired attempt needs a new
  purchase ($175) or a reset ($78, same clock).
- Option 1 drawdown is intraday trailing on equity including open P&L (the most conservative representable form is
  a per-trade high-water mark on equity); Option 2 is EOD on closing balance with a $1,100 soft daily stop (day
  ends, account survives).
- Master payout constraints: 10 trading days per cycle, weekly Wednesday processing (a lag of up to about a week),
  $1,000 minimum, $1,500 cap for payouts 1-3, $2,600 reserve above $50,000, cumulative 40% best-day rule
  including the reserve on payout 1, 100% split on the first $10,000 per trader then 90%.
- Live transition after 3 payouts is discretionary, resets the balance (no profit carried over) and gives a $2,000
  EOD drawdown; live payout terms are not public. Conservative representable form: treat the Master stage as the
  end of the funnel, or the live stage as unknown.
- The trader declares professional or non-professional data status once; professional adds $116 per month.

## 2. Products, commissions and fees, position limits (50K)

Source: RATES (official rate sheet "COMMISSIONS & INSTRUMENTS / All-in rates, per side (USD) / Updated Aug/11/2026",
downloaded today, sha256 35b9ce39..., identical to the Wayback 2026-10-10 copy), and HELP instruments list. The
sheet says: "Per side means the commission is charged for each filled contract on entry and again on exit. Rates
are all-in: exchange and clearing fees are already included. Commissions are part of your P&L and count toward
your drawdown and daily loss limit. 40 instruments available." HELP instruments: "Commissions are charged per side,
which means a commission applies to each filled contract, both on entry and on exit." The same rates apply to
every account type (one sheet; no per-plan sheet found). Platform fees: none per trade; the $100/month
third-party API fee (section 4) and the professional data fee (section 1.2) are monthly.

| Candidate | Allowed | Per side USD | Round trip USD | Quote (RATES line) | Note |
|---|---|---|---|---|---|
| MNG | no | - | - | not on sheet or HELP list | |
| QG | yes | 1.26 | 2.52 | "QG E-mini Natural Gas Futures 1.26 2.52" | |
| NG | yes | 2.26 | 4.52 | "NG Natural Gas (Henry Hub) Futures 2.26 4.52" | |
| MCL | yes | 0.76 | 1.52 | "MCL Micro Crude Oil Futures 0.76 1.52" | |
| QM | yes | 1.96 | 3.92 | "QM E-mini Crude Oil Futures 1.96 3.92" | |
| CL | yes | 2.26 | 4.52 | "CL Crude Oil Futures 2.26 4.52" | |
| MGC | yes | 0.76 | 1.52 | "MGC E-micro Gold Futures 0.76 1.52" | |
| GC | yes | 2.31 | 4.62 | "GC Gold Futures 2.31 4.62" | |
| SIL | no | - | - | not listed | FAQ claims "Every major product also has a micro version" but the sheet has no SIL, MHG, MNG |
| SI | yes | 2.31 | 4.62 | "SI Silver Futures 2.31 4.62" | |
| MHG | no | - | - | not listed | |
| HG | yes | 2.31 | 4.62 | "HG Copper Futures 2.31 4.62" | |
| M6E | yes | 0.50 | 1.00 | "M6E E-micro Euro FX Futures 0.50 1.00" | |
| 6E | yes | 2.36 | 4.72 | "6E Euro FX Futures 2.36 4.72" | HELP calls it "E-mini Euro FX (6E)" |
| M6A | yes | 0.50 | 1.00 | "M6A E-micro Australian Dollar Futures 0.50 1.00" | |
| 6A | yes | 2.36 | 4.72 | "6A Australian Dollar Futures 2.36 4.72" | |
| MET | yes | 0.46 | 0.92 | "MET Micro Ether Futures 0.46 0.92" | |
| ETH | no | - | - | not listed | |
| MBT | yes | 2.76 | 5.52 | "MBT Micro Bitcoin Futures 2.76 5.52" | |
| BTC | no | - | - | not listed | |
| M2K | yes | 0.61 | 1.22 | "M2K Micro E-mini Russell 2000 Futures 0.61 1.22" | |
| RTY | yes | 2.09 | 4.18 | "RTY E-mini Russell 2000 Futures 2.09 4.18" | |
| MYM | yes | 0.61 | 1.22 | "MYM Micro E-mini Dow Jones Index 0.61 1.22" | |
| YM | yes | 2.09 | 4.18 | "YM E-mini Dow ($5) Futures 2.09 4.18" | |
| MNQ | yes | 0.61 | 1.22 | "MNQ Micro E-mini Nasdaq 100 Futures 0.61 1.22" | baseline |
| NQ | yes | 2.09 | 4.18 | "NQ E-mini NASDAQ 100 Futures 2.09 4.18" | |
| 2YY, 5YY, 10Y, 30Y | no | - | - | not listed | no interest-rate products at all |
| ZT, ZF, ZN, ZB | no | - | - | not listed | |
| micro grains (MZC, MZS, MZW, MZL, MZM) | no | - | - | not listed | |
| XC, XK, XW | no | - | - | not listed | |
| ZC | no | - | - | not listed | corn absent from both the sheet and HELP list |
| ZS | yes | 2.86 | 5.72 | "ZS Soybean Futures 2.86 5.72" | |
| ZW | yes | 2.86 | 5.72 | "ZW Wheat Futures 2.86 5.72" | |
| ZL | yes | 2.86 | 5.72 | "ZL Soybean Oil Futures 2.86 5.72" | |
| ZM | yes | 2.86 | 5.72 | "ZM Soybean Meal Futures 2.86 5.72" | |

Other listed products (not candidates): ES, EMD, MES (MES 0.61/1.22), 6B, M6B, 6C, 6J, 6M, 6N, 6S, GF, HE, LE, RB, PL.
Inconsistencies on the firm's own pages: HELP instruments also lists NKD, M6C and ZO, which have no rate on the sheet;
the FAQ says "41 futures contracts", the sheet "40 instruments available".

Position limits at 50K:
- Option 1 (trailing): 7 contracts, "Standard and micro contracts can be traded simultaneously. One standard
  contract is equivalent to ten micro contracts." (HELP rules), so 7 minis or 70 micros or a mix (PRICE footnote
  "1 mini = 10 micros."; the Momentum/Fast Track tables write "7 minis (70 micros)").
- Option 2 (EOD): 2 contracts with Cash on Hand up to $1,500, 4 at $1,501-4,000, 7 at $4,001+ (HELP option-2), same
  10:1 micro ratio; the scaling works in both directions.
- "Open positions must remain within the contract limit for your account." (HELP master-trading-rules). No
  per-product limits beyond the account limit were found.

## 3. Product restrictions: news, hours, flat-by times

| Item | Fact | Source and quote |
|---|---|---|
| News trading | allowed on all products, no blackout windows | FAQ "Can I trade the news?": "Yes. Trade straight through the economic calendar — CPI, FOMC, NFP and every other release. No blackout windows, no forced position closing, no penalties. The only limits are your drawdown and your contract limit." Confirmed today (blx_dev_cms_faq_webfetch_20261021.txt). Pricing banner: "News trading allowed" (PRICE). |
| Product-specific restrictions | none found beyond the product list | no product-level rule on any HELP or FAQ item (grep) |
| Trading day | 5:00 PM CT to 4:00 PM CT next day | HELP rules: "The trading day starts at 5:00 PM and ends at 4:00 PM the following day, North American Central Time (CT)." |
| Flat-by time | 3:59 PM CT, every product, every stage; no overnight or weekend holds | HELP rules: "All positions must be closed by 3:59 PM (CT)." / "Holding positions overnight is strictly prohibited." |
| Hours excluded | only the CME daily maintenance hour (4:00-5:00 PM CT) plus the 3:59-4:00 PM minute; the flat-by applies to every product including those whose CME day ends earlier [inference from the uniform rule] | as above |
| Market halts | firm not responsible for platform or data interruptions | HELP market-halt |

## 4. Automation, API and trading-style rules

| Item | Fact | Source and quote |
|---|---|---|
| Bots and algorithms | permitted (no stage distinction stated, so evaluation and Master alike), but only user-built tools for the account owner's personal use | FAQ "Can I use bots, algos or trade copiers?": "Yes. Bots, algorithms and trade copiers are permitted." / "Only user-built tools intended solely for the account owner’s personal use are permitted. Commercial, shared, rented or publicly distributed automation tools are not allowed." Confirmed today. |
| Third-party software | needs management review and approval before use | TERMS (Oct 2026) lines 268-271: "any third-party algorithm, automated trading software, or other third-party trading technology must be reviewed and approved by the Bulenox management team before use. Approval may be subject to additional requirements or conditions established by Bulenox." |
| API route and fee | direct connection to Rithmic through "an approved third-party API or Trader Composite interface", $100 per month; paying does not approve any algorithm | TERMS lines 275-280: "If you elect to use Trader Composite Software, you shall be required to pay a third-party API/Trader Composite Software fee of one hundred dollars ($100) per month. Payment of this fee permits direct connectivity to the Rithmic platform through an approved third-party API or Trader Composite interface and does not constitute approval of any specific algorithm, strategy, or software."; HELP rules: "If a trader chooses to connect to Rithmic through a Third-Party API or Trader Composite Software, a $100 monthly fee applies." |
| Which API | Rithmic only (accounts live on "Rithmic Paper Trading"); the firm does not name R|API, R|API+ or R|Protocol explicitly; no Tradovate; ProjectX was offered until at least Dec 2025 and is absent today; NinjaTrader 8 via Rithmic (free licence on the Master Account) | HELP rithmic-connection; HELP ninjatrader-connection; FAQ "NinjaTrader 8 comes with a free licence on the Master Account."; blx_wb20251214_old_help_connection.html.txt line 88 "ProjectX Connection"; grep of today's HELP, FAQ and site bundle for ProjectX or Tradovate: 0 hits |
| Banned API | DTC Protocol Bridge API | TERMS line 262: "using “scalping” algorithms, DTC Protocol Bridge API or automated discretional trading in any of the trading environments." |
| Rapid-trade / scalping ban | "scalping" algorithms banned; "hundreds or thousand of rapid trades" by algorithms banned; abuse lets the firm refuse profits. No numeric threshold, no minimum hold time and no order-rate limit published | TERMS lines 261-265: "You agree to not abuse the company provided service programs. It includes but is not limited to using “scalping” algorithms, DTC Protocol Bridge API or automated discretional trading in any of the trading environments. Open and close hundreds or thousand of rapid trades by using any trading algorithms. Implementation of reckless transactions in rough markets to benefit from lack of execution. If abuse is suspected, we reserve the right to refuse to claim any profit." (The phrase "automated discretional trading" is undefined.) |
| Exploiting simulated fills | "reckless transactions in rough markets to benefit from lack of execution" is listed as abuse (same clause) | TERMS line 264 |
| Copy trading | trade copiers permitted (FAQ); one profile per trader, and since Oct 2026 one per household | FAQ; TERMS lines 70-75 |
| Order-rate limit | none published by Bulenox; Rithmic's own limit not found | [not found] |
| "Flipping" payout review | [snippet, review-site pointer only] Trustpilot reviews (early to mid 2026, via WebSearch summary) report Master payouts denied for "flipping trading days", said to be in section 5.6 of the (non-public) Master Account Agreement; one reviewer says support told them at most 2 of 10 trading days may have net profit under $50. Not on any firm page I could read. | WebSearch 2026-10-21 (log.tsv); [unverified] |

## 5. Platforms, sim fill rule, VPS

| Item | Fact | Source and quote |
|---|---|---|
| Platforms | Rithmic R|Trader Pro and "More than 20, including NinjaTrader, R|Trader Pro, Quantower, Sierra Chart, MultiCharts and ATAS"; the help page shows logos (file names) for NinjaTrader, Bookmap, IRT, MotiveWave, Photon Trader, MultiCharts, Sierra Chart, Trade Navigator, TSLab, ScalpTool, QST, Quantower, Medved, OverCharts, QScalp, ATAS, VolFix, InsideEdge, OptimusFlow, Tiger Trade, R|Trader Pro | FAQ; HELP other-platforms (logo image names only, no text) |
| Server | Rithmic Paper Trading, gateway Chicago (Europe/Frankfurt, Tokyo/Singapore offered) | HELP rithmic-connection: "Under  System , select Rithmic Paper Trading." / "Under  Gateway , select Chicago." |
| OCO | on NinjaTrader, OCO is simulated locally (client side); an orphaned leg can open a position | HELP ninjatrader-connection: "OCO — One Cancels Other — functionality is simulated locally on your computer." |
| Sim fill rule for resting limits | not documented by Bulenox. [pointer only, forum] A 2019 post by an account named Rithmic on the Optimus Futures community describes the Rithmic Paper Trading engine as queue-aware: "Our filling algorithm also takes into account when your order was received by the simulator," "Rithmic’s estimated place of the order in the order queue" and "We report a fill when the market trades through your price and when the orders ahead of you in the queue, ... based upon our estimate of your position in the queue and market activity, are depleted" "and there is quantity or opposite side order activity at your price level." | blx_ptr_optimus_rithmic_paper_webfetch_20261021.txt (not evidence under READER_RULES; no official Rithmic page found in 2 searches) |
| VPS | no VPS rule on any Bulenox page (grep of HELP, FAQ, TERMS for "VPS" and "virtual private": 0 hits); 1 WebSearch found nothing | [not found] |

## 6. Reliability

| Item | Fact | Source and quote |
|---|---|---|
| Entity | Bulenox LLC, 1201 N Orange St, Ste 7149, Wilmington, DE 19801; Delaware law, Kent County courts and AAA arbitration | PRICE footer; TERMS lines 387-391, 421 |
| Operating since | at least 2021-06-12 (earliest Wayback capture of bulenox.com, already selling a "Qualification Account" and "Master Account"); Terms dated "Updated July 2021" until Oct 2026; help text stamped "Updated Nov/18/2021" | blx_wb20210612_home.html.txt ("Qualification Account", "Master Account", "Get your first $10,000 without commissions"); blx_wb20261007_terms_prev.txt line 1; blx_wb20251214_old_help_qualification.html.txt line 99. Third-party sites disagree on 2021 vs 2022 [snippet] |
| Payout speed (firm's claim) | Master: weekly on Wednesdays; Fast Track and Momentum: same day | FAQ: "Payout requests on Fast Track and Momentum accounts are processed every day; on a regular Master Account payouts are processed every Wednesday." |
| Payout track record | no figures published by the firm (none found) | [not found] |
| Disputes | [snippet, pointer only] Trustpilot shows about 4.5/5 from about 2K reviews; the main complaint is payout denials for "flipping" (section 4), some reversed after the reviewer pushed back | WebSearch summaries 2026-10-21; [unverified] |
| Regulatory actions | none found. 4 WebSearches (CFTC, NFA, FTC, state attorneys general, SEC; lawsuit, class action, cease and desist) returned no hit on Bulenox. NFA BASIC and state AG sites not queried directly: a search-negative, not a registry check | log.tsv |

### Rule changes in the 12 months to 2026-10-21 (Wayback copies vs today)

1. Billing: Qualification changed from a monthly subscription to one-time. Dec 2025: "The subscription is
   automatically renewed every 30 days until you cancel it yourself." (blx_wb20251214_old_help_qualification.html.txt
   line 209); Apr 2026 home card: "$125/month (Coupon: "$50OFF")" next to "175" (blx_wb20260421_old_home.html.txt
   lines 63-65); today "$175 one-time / Access valid for 30 days". [snippet] eltraderfinanciado.com (affiliate news)
   dates this to 2026-08-17, with the launch of Fast Track and Momentum. Effect: same $175 list price, but a
   30-day hard clock; the old free reset on rebill ("the account will be reset for free on the specific billing
   date. Moreover, the completed trading days will remain.") is gone.
2. Maximum Master accounts: Aug 2025 "Traders can activate up to three (3) Master Accounts simultaneously"
   with unlocking (blx_wb20250807_old_help_master.html.txt line 55); Dec 2025 "up to 11 active Master Accounts"
   (old qualification page line 225); today 5, all at once, shared with Fast Track and Momentum.
3. Automation: Dec 2025 help: "Our company does not provide any kind of algorithms. However, it is not forbidden
   to use them." (old qualification page line 98); today user-built personal tools only, third-party technology
   needs approval (Terms, Oct 2026), and a $100/month third-party API fee.
4. Household rule added to the Terms in Oct 2026 (TERMS lines 70-75): "you are the sole authorized Bulenox
   trader profile holder within your household".
5. Platforms: ProjectX offered in Dec 2025 (old connection page line 88), absent today.
6. Funded Account: Oct 2025 page: balance caps ("50K Funded Account - $5,000", effective April 28, 2025), "All
   active Master Accounts shall be consolidated into a single Funded Account", rewards after "at least five (5)
   or more individual trading days" (blx_wb20251005_old_help_funded.html.txt lines 34-41). Today: each eligible
   Master becomes its own Funded Account with an Initial EOD Drawdown ($2,000 at 50K); no balance cap or
   5-day rule is stated today.
7. Account sizes: $10K and $250K plans (Dec 2025 help, Apr 2026 home) no longer on the pricing page.
8. Payout methods: Aug 2025 "ACH/Wire Transfer, Paypal, Wise"; today ACH or wire and PayPal.
Unchanged: commissions (rate sheets "Updated Sept/25/2024", Wayback 2025-05-03, and "Updated Aug/11/2026" give the
same per-side numbers for every candidate product); Master payout rules (10 days, $1,000 min, $1,500 cap, $2,600
reserve, 40% consistency, 100% of first $10K then 90%, Wednesdays) match Aug 2025; Qualification 50K target $3,000 and drawdown $2,500
(Apr 2026 home card), 50K DLL $1,100 and activation $148 (Dec 2025 help), and the reset price $78 (Dec 2025 help line
209: "If the trader wants to reset the account at any other time, it will cost $78.").
Which of these count as "material adverse" is the lead's call.

## 7. Eligibility: British Columbia and Canada

| Item | Fact | Source and quote |
|---|---|---|
| Canada | accepted: not on the restricted-country list (about 100 countries listed, Canada absent); no province-level exclusion found | FAQ "Is my country supported?" (Wayback 2026-10-08; today's WebFetch: "Canada does not appear in the restricted list"); grep "Canada" in FAQ, HELP and TERMS: 0 hits |
| British Columbia | no rule naming BC or any province | [absence] |
| KYC | Withdrawal Information Form, valid ID, hand-signed W-8BEN for non-US persons; names and payment details must match | HELP withdrawal-rules: "Every trader must complete the Bulenox Withdrawal Information Form and include a valid identification document." / "non-U.S. persons: completed and signed W-8BEN;" |
| Methods | ACH or wire transfer, PayPal; no Bulenox transfer fee (banks or PayPal may charge) | HELP: "Bulenox does not charge a transfer fee. However, the receiving bank, intermediary bank or PayPal may apply its own fees." |
| Currency | not stated (prices and payouts quoted in USD; no CAD option found) | [not found] |
| Tax forms | non-US persons: W-8BEN; independent-contractor status | FAQ "How am I taxed?" |
| Purchase methods | credit or debit card, PayPal, crypto | HELP payment-methods |

## 8. Facts by spec criterion (pointers for the lead; no scores)

- E (economics): $175 one-time per 30-day Qualification, $78 reset (same clock), $148 activation; target $3,000;
  $2,500 drawdown (Option 1 trailing intraday incl. open P&L, or Option 2 EOD with a $1,100 soft DLL); Master payout
  rules in 1.3; commissions per product in section 2 (all-in, per side, include exchange and clearing fees).
- D: maximum loss limit at 50K = $2,500 (both options; Master the same; live Funded $2,000 EOD). DLL: none
  (Option 1) or $1,100 (Option 2). Position limit 7 minis or 70 micros (Option 2: 2/4/7 by Cash on Hand).
- R: news trading explicitly allowed for every release; no product-specific windows; one firm-wide flat-by at
  3:59 PM CT and no overnight holds.
- A: automation permitted ("Bots, algorithms and trade copiers are permitted") but limited to user-built personal
  tools, third-party technology needs management approval, direct Rithmic API access costs $100/month; Terms ban
  "scalping" algorithms and "hundreds or thousand of rapid trades" with no number; no published rate limit or
  minimum hold; DTC Protocol Bridge banned; undefined "automated discretional trading" ban.
- F: no fill rule published by Bulenox; Rithmic Paper Trading's queue-estimate rule is known only from a forum
  post (pointer).
- P: no native Bulenox API; automation through Rithmic via an approved third-party API ($100/month) or platform
  scripts (NinjaTrader 8 free on Master); OCO on the API: not stated (NinjaTrader OCO is client-side); VPS: not
  stated; rate limit: not stated. Rithmic gateway Chicago.
- Rel: operating since at least June 2021 (over 5 years); payout-denial complaints ("flipping") from review sites
  only (pointer); rule changes listed in section 6; no regulatory action found (search-negative).
- Gates: Canada accepted (not on the restricted list; no BC rule). Products not listed (gate): MNG, SIL, MHG, ETH,
  BTC, all eight rates candidates, the micro grains, XC, XK, XW, ZC.
- Canadian tax line (not scored): Bulenox treats traders as independent contractors and collects a W-8BEN from
  non-US persons; it issues no Canadian slip (none mentioned).

## 9. Not found, not verified, deviations

- Not found on any firm page: sim fill rule; VPS policy; order-rate limit; which Rithmic API product (R|API,
  R|API+, R|Protocol) the "approved third-party API" means; whether OCO or brackets are native on that API; live
  Funded Account rules beyond the $2,000 Initial EOD Drawdown (DLL, split, caps, payout days; governed by the
  non-public Funded Account Agreement); payout currency for Canadians; the coupon's discount amount; the Master
  Account Agreement (including the reported section 5.6 "flipping" rule); a published payout track record.
- Not verified from full text: founding year (2021 vs 2022 on third-party sites); Trustpilot score and complaints
  (search snippets; review sites are pointers only); the Aug 2026 date of the billing change (affiliate news, via
  search snippet).
- Regulator checks: WebSearch only; NFA BASIC, CFTC site search and state AG databases not queried directly.
- Internal inconsistencies on firm pages: professional data fee $116/month (pricing, help status item) vs "$112
  per exchange" (help Rithmic item); 40 instruments (rate sheet) vs 41 (FAQ) vs NKD, M6C, ZO listed in help but
  without a rate.
- Deviation fetches (WebFetch, once each, 2026-10-21; listed in pages/A2_bulenox/DO_NOT_COMMIT.txt): the pricing
  page and two filtered requests to the site's own CMS endpoint (help items and FAQ items), because today's values
  could only come from those pages; WebFetch returns model-extracted text, so raw quotes come from the Wayback
  copies of the same content. One official PDF (rate sheet) downloaded once by curl. No Scrapling and no curl on
  bulenox.com HTML.
- Wayback route notes: one CDX request hit "Internet Archive services are temporarily offline" and was retried;
  four first downloads of CMS URLs failed because curl treated "[ ]" as globs (fixed with -g; marked in log.tsv).
- WebSearch calls used: 13 of 40.
