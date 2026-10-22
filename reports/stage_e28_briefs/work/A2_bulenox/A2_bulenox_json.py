import json
P = "reports/stage_e28_briefs/pages/A2_bulenox/"
HELP = P + "blx_wb20260928_cms_help_items.txt"; HELPT = P + "blx_dev_cms_help_webfetch_20261021.txt"
FAQ = P + "blx_wb20261008_cms_faq_items.txt"; PRICEJS = P + "blx_wb20260928_index.js"
PRICE = P + "blx_wb20261009_accounts-pricing_eod"; PRICET = P + "blx_dev_pricing_webfetch_20261021.txt"
RATES = P + "blx_rates_20261021.txt"; TERMS = P + "blx_terms_wb20261019.txt"
def f(value, unit, src, quote, note=""):
    return {"value": value, "unit": unit, "source_file": src, "quote": quote, "note": note}
plan = {
 "plan_name": f("Qualification Account $50,000 (first tab, first 50K card); risk model Option 1 Trailing (listed first) or Option 2 EOD, chosen at purchase and locked", None, PRICE, "Option 1 · No scaling ... Option 2 · Scaling plan · Daily loss limit ... This choice is locked for the life of the account.", "Lead chooses which option to simulate; price identical"),
 "price": f(175, "USD one-time", PRICEJS, "{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}", "today confirmed: " + PRICET),
 "billing": f("one-time; 30 days of access; no renewal", None, HELP, "Your account is paid once and expires automatically at the end of its access period — no renewal and no recurring charge.", "changed from 30-day auto-renewing subscription (Dec 2025)"),
 "access_period": f(30, "calendar days", PRICE, "Access valid for 30 days", "hard clock per purchase; reset does not extend it"),
 "profit_target": f(3000, "USD", PRICE, "Profit target $3,000", ""),
 "max_loss_limit_option1": f(2500, "USD trailing intraday (real time, incl. unrealized P&L and commissions)", HELP, "The trailing drawdown follows your account’s highest value throughout the trading day, including both realized and unrealized (open) profits. It is calculated in real time and includes commissions.", "Drawdown up to $2,500 on the card"),
 "max_loss_limit_option2": f(2500, "USD end-of-day (closing balance)", HELP, "The End-of-Day (EOD) drawdown is updated once per trading day, after the market closes.", ""),
 "daily_loss_limit_option1": f(None, None, PRICE, "No daily loss limit", ""),
 "daily_loss_limit_option2": f(1100, "USD soft (trading disabled for rest of day, not a violation)", HELP, "If your Daily Loss Limit is reached, trading is disabled for the rest of the trading day. This is not considered a rule violation", "table row $50,000 $1,100"),
 "consistency_rule": f(None, None, HELP, "", "none found for the Qualification stage (absence after grep)"),
 "minimum_days": f(0, "days", HELP, "There are no minimum trading days required to obtain a Master Account.", ""),
 "maximum_days": f(None, None, FAQ, "There is no minimum and no maximum number of trading days", "but the 30-day access period applies"),
 "reset_fee": f(78, "USD", HELP, "A reset costs $78 and returns your balance to its starting value", "clears P&L and trading days; does not extend 30-day access"),
 "activation_fee": f(148, "USD one-time (Master Account)", HELP, "Each Master Account requires a separate one-time activation fee", "table $50,000 $148; same for both options; today confirmed " + HELPT),
 "contracts_option1": f(7, "contracts (minis; 1 mini = 10 micros)", PRICE, "Contracts 7 ... 1 mini = 10 micros.", ""),
 "contracts_option2": f("2 (Cash on Hand up to $1,500), 4 ($1,501-4,000), 7 ($4,001+)", "contracts", HELP, "$50,000 | Up to $1,500: 2 • $1,501–4,000: 4 • $4,001+: 7", "scales both directions"),
 "flat_by": f("15:59 CT; no overnight", None, HELP, "All positions must be closed by 3:59 PM (CT).", "Holding positions overnight is strictly prohibited."),
 "pass_review": f("manual review before Master; not automatic", None, HELP, "Reaching the profit target does not automatically open a Master Account. Your Qualification Account must first be reviewed.", ""),
 "data_fee_professional": f(116, "USD/month", PRICE, "CME, CBOT, NYMEX and COMEX data is billed at $116/month on top of your account.", "help Rithmic item says $112 per exchange; non-professional free"),
}
master = {
 "stage_type": f("simulated (Master Account, Rithmic Paper Trading)", None, HELP, "Funded Account  — a real brokerage account funded by Bulenox and traded with real money.", "inference: only Funded is called real; Fast Track (Master-level) is 'a simulated funded environment' (FAQ)"),
 "drawdown": f(2500, "USD, same model as Qualification option; initial threshold 47,500; locks at 50,100 when account value reaches 52,600", HELP, "$50,000 | $2,500 | $47,500 | $50,100 | $52,600", "today confirmed"),
 "daily_loss_limit": f("Option 1 none; Option 2 1,100 soft, removed once drawdown locks", "USD", HELP, "The Daily Loss Limit is permanently removed once the EOD Drawdown locks at the starting balance + $100.", ""),
 "payout_trading_days": f(10, "trading days per payout cycle", HELP, "complete at least 10 individual trading days;", "next 10 count after previous payout completed"),
 "payout_min": f(1000, "USD", HELP, "The minimum payout amount is $1,000.", ""),
 "payout_max_first3": f(1500, "USD per payout, payouts 1-3", HELP, "$50,000 | $1,500", "no cap after the third"),
 "safety_threshold_reserve": f(2600, "USD above starting balance", HELP, "To request the minimum payout of $1,000, the account balance must be at least $50,000 + $2,600 + $1,000 =  $53,600 .", ""),
 "consistency": f(40, "% best day / Total P&L, cumulative over the Master period; reserve included on payout 1", HELP, "Your most profitable trading day must not represent more than 40% of your Total P&L for the applicable payout period.", "The calculation does not reset after a payout"),
 "split": f("100% of first $10,000 per trader profile, then 90%", None, HELP, "You receive 100% of the first $10,000 paid from your profile.", "the trader receives 90% of each additional payout;"),
 "frequency": f("weekly, Wednesdays; request by Fri 23:59 CT", None, HELP, "Payouts are processed once a week, on Wednesdays.", ""),
 "max_accounts": f(5, "active Master-level accounts (Master, Fast Track, Momentum Master combined)", HELP, "A trader may hold up to five active Master-level accounts under one Bulenox profile and one Rithmic User ID.", "Qualification unlimited; one profile per household since Oct 2026 (TERMS lines 70-75)"),
 "breach": f("account closed; Master reset priced individually", None, HELP, "The reset fee is calculated individually for each account.", ""),
 "activation_link_validity": f(7, "days", HELP, "Once an activation link is issued, it remains valid for 7 days.", "a Master Account queue exists before the link"),
}
funded = {
 "entry": f("after 3 successful Master payouts, at Bulenox's discretion", None, HELP, "The transition is completed at Bulenox’s discretion and is not automatic after the third payout.", ""),
 "carry_over": f(None, None, HELP, "Profits, balance, equity or other monetary amounts accumulated in your Master-level Account do not transfer to the Funded Account.", ""),
 "initial_eod_drawdown": f(2000, "USD", HELP, "$50,000 ... $2,000 (Initial EOD Drawdown table)", "today confirmed"),
 "live_rules": f(None, None, "", "", "DLL, split, caps, payout days not public (Funded Account Agreement)"),
}
rates = {"QG":(1.26,2.52,"E-mini Natural Gas Futures"),"NG":(2.26,4.52,"Natural Gas (Henry Hub) Futures"),"MCL":(0.76,1.52,"Micro Crude Oil Futures"),"QM":(1.96,3.92,"E-mini Crude Oil Futures"),"CL":(2.26,4.52,"Crude Oil Futures"),"MGC":(0.76,1.52,"E-micro Gold Futures"),"GC":(2.31,4.62,"Gold Futures"),"SI":(2.31,4.62,"Silver Futures"),"HG":(2.31,4.62,"Copper Futures"),"M6E":(0.50,1.00,"E-micro Euro FX Futures"),"6E":(2.36,4.72,"Euro FX Futures"),"M6A":(0.50,1.00,"E-micro Australian Dollar Futures"),"6A":(2.36,4.72,"Australian Dollar Futures"),"MET":(0.46,0.92,"Micro Ether Futures"),"MBT":(2.76,5.52,"Micro Bitcoin Futures"),"M2K":(0.61,1.22,"Micro E-mini Russell 2000 Futures"),"RTY":(2.09,4.18,"E-mini Russell 2000 Futures"),"MYM":(0.61,1.22,"Micro E-mini Dow Jones Index"),"YM":(2.09,4.18,"E-mini Dow ($5) Futures"),"MNQ":(0.61,1.22,"Micro E-mini Nasdaq 100 Futures"),"NQ":(2.09,4.18,"E-mini NASDAQ 100 Futures"),"ZS":(2.86,5.72,"Soybean Futures"),"ZW":(2.86,5.72,"Wheat Futures"),"ZL":(2.86,5.72,"Soybean Oil Futures"),"ZM":(2.86,5.72,"Soybean Meal Futures")}
order = ["MNG","QG","NG","MCL","QM","CL","MGC","GC","SIL","SI","MHG","HG","M6E","6E","M6A","6A","MET","ETH","MBT","BTC","M2K","RTY","MYM","YM","MNQ","NQ","2YY","5YY","10Y","30Y","ZT","ZF","ZN","ZB","MZC","MZS","MZW","MZL","MZM","XC","XK","XW","ZC","ZS","ZW","ZL","ZM"]
products = {}
for c in order:
    if c in rates:
        ps, rt, name = rates[c]
        products[c] = {"allowed": f(True, None, RATES, f"{c} {name} {ps:.2f} {rt:.2f}", "listed"),
                       "commission_per_side": f(ps, "USD all-in per side (exchange and clearing included)", RATES, f"{c} {name} {ps:.2f} {rt:.2f}", "rate sheet Updated Aug/11/2026; unchanged since Sept/25/2024 sheet"),
                       "commission_round_trip": f(rt, "USD all-in round turn", RATES, f"{c} {name} {ps:.2f} {rt:.2f}", "")}
    else:
        products[c] = {"allowed": f(False, None, RATES, "", "not on the rate sheet ('40 instruments available') nor the help instruments list"),
                       "commission_per_side": f(None, None, "", "", "not listed"), "commission_round_trip": f(None, None, "", "", "not listed")}
fees_note = f("Rates are all-in: exchange and clearing fees are already included.", None, RATES, "Per side means the commission is charged for each filled contract on entry and again on exit. Rates are all-in: exchange and clearing fees are already included.", "plus $100/month if connecting via third-party API; professional data $116/month")
position_limits = {
 "option1": f("7 minis or 70 micros (mix allowed, 1:10)", None, HELP, "Standard and micro contracts can be traded simultaneously. One standard contract is equivalent to ten micro contracts.", ""),
 "option2": f("2 / 4 / 7 by Cash on Hand (<=1,500; 1,501-4,000; 4,001+), same 1:10 ratio", None, HELP, "$50,000 | Up to $1,500: 2 • $1,501–4,000: 4 • $4,001+: 7", ""),
}
restrictions = {
 "news": f("allowed, no blackout windows", None, FAQ, "Yes. Trade straight through the economic calendar — CPI, FOMC, NFP and every other release. No blackout windows, no forced position closing, no penalties.", "today confirmed"),
 "product_specific": f(None, None, HELP, "", "none found"),
 "trading_day": f("17:00 CT to 16:00 CT next day", None, HELP, "The trading day starts at 5:00 PM and ends at 4:00 PM the following day, North American Central Time (CT).", ""),
 "flat_by": f("15:59 CT all products all stages; no overnight", None, HELP, "All positions must be closed by 3:59 PM (CT).", ""),
}
automation = {
 "bots_allowed": f("yes, user-built personal tools only; both stages (no distinction stated)", None, FAQ, "Yes. Bots, algorithms and trade copiers are permitted.", "Only user-built tools intended solely for the account owner’s personal use are permitted. Commercial, shared, rented or publicly distributed automation tools are not allowed."),
 "third_party_approval": f("required", None, TERMS, "any third-party algorithm, automated trading software, or other third-party trading technology must be reviewed and approved by the Bulenox management team before use.", "Terms Updated October 2026, lines 268-271"),
 "api": f("Rithmic via an approved third-party API or Trader Composite interface; R|API product not named; no Tradovate; ProjectX gone since Dec 2025", None, TERMS, "Payment of this fee permits direct connectivity to the Rithmic platform through an approved third-party API or Trader Composite interface", ""),
 "api_fee": f(100, "USD/month", TERMS, "you shall be required to pay a third-party API/Trader Composite Software fee of one hundred dollars ($100) per month.", ""),
 "banned": f("scalping algorithms; DTC Protocol Bridge API; 'automated discretional trading'; hundreds or thousands of rapid trades; reckless trades exploiting lack of execution", None, TERMS, "using “scalping” algorithms, DTC Protocol Bridge API or automated discretional trading in any of the trading environments. Open and close hundreds or thousand of rapid trades by using any trading algorithms. Implementation of reckless transactions in rough markets to benefit from lack of execution.", "no numeric threshold; profits may be refused"),
 "order_rate_limit": f(None, None, "", "", "not published"),
 "minimum_hold": f(None, None, "", "", "not published"),
 "flipping_review": f("[unverified] payout denials for 'flipping trading days' reported on Trustpilot; said to be Master Agreement s.5.6", None, "", "", "search-snippet pointer only"),
}
platforms = {
 "platforms": f("R|Trader Pro, NinjaTrader 8 (free licence on Master), Quantower, Sierra Chart, MultiCharts, ATAS and others (20+)", None, FAQ, "More than 20, including NinjaTrader, R|Trader Pro, Quantower, Sierra Chart, MultiCharts and ATAS.", ""),
 "server": f("Rithmic Paper Trading, Chicago gateway", None, HELP, "Under  System , select Rithmic Paper Trading.", ""),
 "oco": f("NinjaTrader OCO simulated client-side", None, HELP, "OCO — One Cancels Other — functionality is simulated locally on your computer.", "API OCO/bracket not stated"),
 "sim_fill_rule": f(None, None, P + "blx_ptr_optimus_rithmic_paper_webfetch_20261021.txt", "We report a fill when the market trades through your price and when the orders ahead of you in the queue, ... based upon our estimate of your position in the queue and market activity, are depleted", "not documented by Bulenox; forum post by an account named Rithmic (2019) is a pointer only"),
 "vps": f(None, None, "", "", "no VPS rule on any firm page"),
}
reliability = {
 "operating_since": f("2021-06-12 or earlier", None, P + "blx_wb20210612_home.html.txt", "Qualification Account ... Master Account ... Get your first $10,000 without commissions", "earliest Wayback capture; third-party sites say 2021 or 2022 [snippet]"),
 "entity": f("Bulenox LLC, Wilmington DE", None, PRICE, "Bulenox LLC 1201 N Orange St, Ste 7149 Wilmington, DE 19801", ""),
 "payout_speed_claim": f("Master weekly (Wednesdays); Fast Track and Momentum same day", None, FAQ, "on a regular Master Account payouts are processed every Wednesday.", "firm claim"),
 "disputes": f("[unverified] Trustpilot ~4.5/5 (~2K reviews); 'flipping' payout denials reported in 2026", None, "", "", "search snippets; review sites are pointers only"),
 "regulatory_actions": f("none found", None, P + "log.tsv", "", "4 WebSearches; NFA BASIC/CFTC/state AG databases not queried directly"),
}
rule_changes = [
 f("billing: monthly auto-renew -> one-time $175 with 30-day access", None, P + "blx_wb20251214_old_help_qualification.html.txt", "The subscription is automatically renewed every 30 days until you cancel it yourself.", "line 209; [snippet] affiliate news dates it 2026-08-17"),
 f("max Master accounts: 3 (Aug 2025) / 11 (Dec 2025) -> 5", None, P + "blx_wb20251214_old_help_qualification.html.txt", "Trader could have unlimited Qualification Accounts and up to 11 active Master Accounts.", "line 225"),
 f("automation: 'not forbidden' -> user-built only, third-party approval, $100/month API fee", None, P + "blx_wb20251214_old_help_qualification.html.txt", "Our company does not provide any kind of algorithms. However, it is not forbidden to use them.", "line 98"),
 f("household single-profile rule added (Terms Oct 2026)", None, TERMS, "you are the sole authorized Bulenox trader profile holder within your household", "lines 70-75"),
 f("ProjectX platform removed", None, P + "blx_wb20251214_old_help_connection.html.txt", "ProjectX Connection", "line 88; absent today"),
 f("Funded: single consolidated account with balance caps and 5-day reward rule -> one Funded Account per eligible Master with Initial EOD Drawdown", None, P + "blx_wb20251005_old_help_funded.html.txt", "All active Master Accounts shall be consolidated into a single Funded Account.", "lines 34-41"),
 f("$10K and $250K sizes dropped; Wise payout method dropped", None, P + "blx_wb20250807_old_help_master.html.txt", "Withdrawal could be requested via ACH/Wire Transfer, Paypal, Wise.", "line 99"),
]
eligibility = {
 "canada": f(True, None, FAQ, "We are proud to support traders in over 100 countries worldwide.", "Canada absent from restricted list (Wayback 2026-10-08 and today)"),
 "british_columbia": f(True, None, FAQ, "", "no province-level rule found"),
 "kyc": f("Withdrawal Information Form, valid ID, hand-signed W-8BEN", None, HELP, "Every trader must complete the Bulenox Withdrawal Information Form and include a valid identification document.", ""),
 "payout_methods": f("ACH or wire transfer, PayPal; no Bulenox transfer fee", None, HELP, "Bulenox does not charge a transfer fee.", ""),
 "payout_currency": f(None, None, "", "", "not stated (USD amounts)"),
}
out = {"schema": "e28-A2-firm-1", "firm": "Bulenox", "as_of": "2026-10-21", "root": "A2_bulenox",
       "fetch_log": P + "log.tsv", "plan_50k": plan, "master_stage": master, "funded_stage": funded,
       "products": products, "fees_note": fees_note, "position_limits_50k": position_limits,
       "restrictions": restrictions, "automation": automation, "platforms": platforms,
       "reliability": reliability, "rule_changes_12m": rule_changes, "eligibility": eligibility,
       "websearch_calls": 13}
json.dump(out, open("reports/stage_e28_briefs/A2_firm_bulenox.json", "w"), indent=1, ensure_ascii=False)
print(len(products), sum(1 for v in products.values() if v["allowed"]["value"]))
