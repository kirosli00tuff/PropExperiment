"""A2_topstep: build A2_firm_topstep.json and verify every quote against its saved source file.

Each fact is {"value","unit","source_file","quote","note"}. A quote may hold several fragments joined by ' ... ';
each fragment must appear in the source text after normalisation (pipes dropped, whitespace collapsed).
Prints counts and any quote that fails.
"""
import json
import re
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PG = "reports/stage_e28_briefs/pages/A2_topstep/"
OUT = REPO / "reports/stage_e28_briefs/A2_firm_topstep.json"


def F(value, unit, src, quote, note=""):
    return {"value": value, "unit": unit, "source_file": (PG + src) if src else None, "quote": quote, "note": note}


def plan():
    return {
        "plan_name": F("50K Trading Combine, Standard Path", None, "ts_14289835.html.txt",
                       "Standard Path ... No Activation Fee Path ... 50K ... $49/month ... $95/month",
                       "First 50K plan on the pricing page; www card shows $49 and $85 (=$95-$10 DLL discount, inference)."),
        "price_monthly_standard": F(49, "USD/month", "ts_14289835.html.txt", "$49/month", "recurring every 30 days"),
        "price_monthly_no_activation_fee": F(95, "USD/month", "ts_14289835.html.txt", "$95/month"),
        "naf_dll_discount": F(10, "USD/month", "ts_14289835.html.txt", "$10 off → 50K ... Discount recurs monthly.",
                              "No Activation Fee path only, DLL added at purchase"),
        "billing": F("monthly, rebills every 30 days, no time limit", None, "ts_8284121.html.txt",
                     "It Rebills every 30 days from your original sign-up date. ... No time limit for passing."),
        "profit_target": F(3000, "USD", "ts_8284208.html.txt", "$50K ... $3,000 ... Less than $1,650"),
        "mll_amount": F(2000, "USD", "ts_8284204.html.txt", "You start a 50K Trading Combine. Balance: $50,000. MLL: $48,000."),
        "mll_type": F("trailing on end-of-day balance, monitored intraday on realized+unrealized P&L, locks at starting balance",
                      None, "ts_8284204.html.txt",
                      "It rises as your end-of-day balance grows, but never moves down. Once it reaches your starting balance, it locks permanently. ... Both realized and unrealized P&L count toward it."),
        "dll": F("optional; 1000 if added at purchase (fixed, carries into XFA); not a violation", "USD", "ts_10490293.html.txt",
                 "$50K Account: $1,000 ... Daily Loss Limit at checkout is fixed (no changes later) ... Triggering it is not a rule violation"),
        "consistency": F(0.55, "best day / profit target", "ts_8284208.html.txt",
                         "Your single best day of profit must stay at or below 55% of your Profit Target. If it exceeds that, your Profit Target increases. ... Best Day ÷ 0.55 = Total Profit Needed."),
        "min_days": F(2, "days", "ts_8284197.html.txt", "You can pass in as few as two days"),
        "time_limit": F(None, None, "ts_8284121.html.txt", "No time limit for passing."),
        "max_position": F("5 minis / 50 micros (10:1)", "contracts", "ts_8284197.html.txt", "Micros and minis count at a 10:1 ratio."),
        "reset_fee_standard": F(49, "USD", "ts_14289835.html.txt", "Reset Pricing", "table: 50K $49 Standard, $95 NAF"),
        "reset_rules": F("1 free credit per rebill; max 2 resets/account/day; reset pushes rebill 30 days", None, "ts_8284128.html.txt",
                         "Every monthly Rebill adds 1 Reset Credit to your Reset Bank. ... Limit: 2 Resets per account each day. ... Resetting your account pushes your Rebill date out 30 days from the date of purchase."),
        "activation_fee_standard": F(149, "USD one-time per XFA", "ts_8284217.html.txt", "$149 one-time activation fee per XFA"),
        "activation_fee_naf": F(0, "USD", "ts_8284217.html.txt", "No activation fee"),
        "combine_sim_fee_conflict": F("$3.70/lot (LFA costs page) vs per-product table (commissions page)", None, "ts_8284229.html.txt",
                                      "In the Trading Combine®, a $3.70/lot simulated fee is charged to emulate these real-world costs.",
                                      "Commissions page: 'These fees apply when trading the Trading Combine, Express Funded Account, and Live Funded Account.'"),
    }


def funded():
    return {
        "xfa_sim_or_live": F("simulated", None, "ts_8284215.html.txt",
                             "The Express Funded Account® (XFA) is the simulated funded-level account you earn after passing your Trading Combine."),
        "xfa_start_balance": F(0, "USD", "ts_8284215.html.txt", "Your balance starts at $0 and grows from your trading profits."),
        "xfa_mll": F("-2000 trailing on EOD balance, locks at 0 when balance reaches 2000; 0 after first payout", "USD", "ts_8284204.html.txt",
                     "For a 50K XFA, your MLL starts at -$2,000 and trails upward. Once your balance reaches $2,000, the MLL locks at $0 permanently. ... After your first Payout: Your MLL is set to $0 regardless of where it was before."),
        "xfa_dll": F("optional (1000 if chosen)", "USD", "ts_8284215.html.txt", "Daily Loss Limit (DLL) ... Optional"),
        "payout_paths": F("Standard: 5 winning days >= 150; Consistency: 3 traded days, best day <= 40%", None, "ts_8284233.html.txt",
                          "5 winning days of $150+ Net P&L. Days don't need to be consecutive. A day locks in at 4:00 PM CT. ... 3 trading days with at least 1 trade per day."),
        "payout_frac": F(0.5, "of balance per request", "ts_8284233.html.txt", "Max Payout per request: 50% of your account balance up to the cap below."),
        "payout_cap_50k_standard": F(2000, "USD per request", "ts_8284233.html.txt", "$50K ... $2,000 ... $3,000"),
        "payout_cap_50k_consistency": F(3000, "USD per request", "ts_8284233.html.txt", "$50K ... $2,000 ... $3,000"),
        "payout_cap_50k_with_dll": F({"standard": 4000, "consistency": 6000}, "USD per request", "ts_8284233.html.txt",
                                     "Traders who voluntarily add a Daily Loss Limit to their account unlock double per-request payout caps.",
                                     "Only if DLL was added at Combine purchase; promotion from 2026-06-02, no end date"),
        "payout_positive_since_last": F(True, None, "ts_8284233.html.txt", "You must have earned at least $0.01 since your last Payout. Your first Payout is exempt."),
        "profit_split": F(0.9, "trader share", "ts_8284233.html.txt", "90/10 profit split — you keep 90%"),
        "payout_min": F(125, "USD", "ts_8284233.html.txt", "Minimum Payout: $125"),
        "payout_fees": F({"ach": 30, "wire": 30, "wise": 0, "aeropay": 0}, "USD", "ts_8284233.html.txt",
                         "No Topstep fee for Aeropay or Wise, but your bank or those services may charge their own fees.",
                         "ACH and Wire/SWIFT rows show $30"),
        "payout_approval_time": F("1-3 business days internal approval", None, "ts_8284233.html.txt", "Internal approval can take 1-3 business days."),
        "scaling_50k": F([{"below": 1500, "lots": 2}, {"from": 1500, "to": 2000, "lots": 3}, {"above": 2000, "lots": 5}], "mini-equivalents",
                         "ts_scaling_xfa_charts.png", None, "Image (sha256 55ec76b4b293..., identical to E.19 copy), read visually; page ts_8284223: 'Your max contracts do not increase mid-session.'"),
        "max_xfas": F(5, "accounts", "ts_8284215.html.txt", "You can hold up to 5 active XFAs at a time."),
        "inactivity": F(30, "days", "ts_8284215.html.txt", "XFAs with no trading activity for more than 30 days may be closed."),
        "back2funded": F({"price": 599, "max": 2, "window_days": 30, "dll_discount": 50}, "USD", "ts_12060405.html.txt",
                         "Back2Funded gives you up to 2 Reactivations per account if you lose your Express Funded Account® (XFA) before your first Payout. ... $50K XFA ... $599"),
        "lfa_callup": F("discretionary; 0.71% of 2025 XFA participants", None, "ts_www_about-us.html.txt",
                        "(d) 0.71% of individual participants trading in an Express Funded Account were called up to a Live Funded Account."),
        "lfa_api": F(False, None, "ts_11187768.html.txt", "No, Live funded accounts are not allowed to trade through the ProjectX API."),
        "lfa_dll_50k": F(2000, "USD", "ts_10657969.html.txt", "Live Funded Accounts start with a Daily Loss Limit (DLL) based on account size:"),
        "lfa_start": F("20% tradable (min 10,000), 80% reserve in 4 x 25% per 3,000 profit", None, "ts_10657969.html.txt",
                       "20% available to trade immediately — minimum $10,000 ... 80% held in Reserve — released in 4 increments of 25% as you hit profit thresholds"),
    }


PRODUCTS = {  # code: (listed, rt_usd, label in permitted list or None, note)
    "MNG": (True, 1.92, "Micro Henry Hub Natural Gas (MNG)", "exchange fee raised 2026-10-01"),
    "QG": (True, 2.02, "E-mini Natural Gas (QG)", ""),
    "NG": (True, 4.22, "Natural Gas (NG)", ""),
    "MCL": (True, 1.72, "Micro Crude Oil (MCL)", "exchange fee raised 2026-10-01; volatility cap 30 at 50K"),
    "QM": (True, 3.42, "E-mini Crude Oil (QM)", "volatility cap 3 at 50K"),
    "CL": (True, 4.02, "Crude Oil (CL)", "volatility cap 3 at 50K"),
    "MGC": (True, 1.92, "Micro Gold (MGC)", "volatility cap 30 at 50K; Tier 1 cap"),
    "GC": (True, 4.32, "Gold (GC)", "volatility cap 3 at 50K; Tier 1 no new opens"),
    "SIL": (True, 2.72, "Micro Silver (SIL)", "counts as 2 micros; volatility cap 2 at 50K"),
    "SI": (True, 4.32, "Silver (SI)", "listed but currently 0 contracts (volatility restriction)"),
    "MHG": (True, 1.92, "Micro Copper (MHG)", "volatility cap 2 at 50K"),
    "HG": (True, 4.32, "Copper (HG)", "listed but currently 0 contracts (volatility restriction)"),
    "M6E": (True, 1.00, "Micro Euro FX (M6E)", ""),
    "6E": (True, 4.22, "Euro FX (6E)", ""),
    "M6A": (True, 1.00, "Micro AUD/USD (M6A)", ""),
    "6A": (True, 4.22, "Australian $ (6A)", ""),
    "MET": (True, 0.72, "Micro Ether (MET)", "capped at mini-equivalent lots"),
    "ETH": (False, None, None, "not on permitted list or fee table"),
    "MBT": (True, 2.82, "Micro Bitcoin (MBT)", "capped at mini-equivalent lots"),
    "BTC": (False, None, None, "not listed"),
    "M2K": (True, 1.22, "Micro E-mini Russell 2000 (M2K)", "Tier 1 cap 3 at 50K Combine"),
    "RTY": (True, 3.78, "E-mini Russell 2000 (RTY)", "Tier 1 no new opens"),
    "MYM": (True, 1.22, "Micro Mini-DOW (MYM)", "Tier 1 cap"),
    "YM": (True, 3.78, "Mini-DOW (YM)", "Tier 1 no new opens"),
    "MNQ": (True, 1.22, "Micro E-mini NASDAQ 100 (MNQ)", "Tier 1 cap"),
    "NQ": (True, 3.78, "E-mini NASDAQ 100 (NQ)", "Tier 1 no new opens"),
    "2YY": (False, None, None, "micro yield futures not listed"),
    "5YY": (False, None, None, "not listed"),
    "10Y": (False, None, None, "not listed"),
    "30Y": (False, None, None, "not listed"),
    "ZT": (True, 2.32, "2-Year Note (ZT)", ""),
    "ZF": (True, 2.32, "5-Year Note (ZF)", ""),
    "ZN": (True, 2.62, "10-Year Note (ZN)", ""),
    "ZB": (True, 2.76, "30-Year Bond (ZB)", ""),
    "MZC": (False, None, None, "micro grains not listed"),
    "MZS": (False, None, None, "not listed"),
    "MZW": (False, None, None, "not listed"),
    "MZL": (False, None, None, "not listed"),
    "MZM": (False, None, None, "not listed"),
    "XC": (False, None, None, "mini grains not listed"),
    "XK": (False, None, None, "not listed"),
    "XW": (False, None, None, "not listed"),
    "ZC": (True, 5.28, "Corn (ZC)", "special hours"),
    "ZS": (True, 5.28, "Soybeans (ZS)", "special hours; fee label 'Soybean (ZS)'"),
    "ZW": (True, 5.28, "Wheat (ZW)", "special hours"),
    "ZL": (True, 5.28, "Soybean Oil (ZL)", "special hours"),
    "ZM": (True, 5.28, "Soybean Meal (ZM)", "special hours"),
}


def products():
    out = {}
    for code, (listed, rt, label, note) in PRODUCTS.items():
        out[code] = {
            "allowed": F(listed, None, "ts_8284206.html.txt", label if listed else None,
                         note if listed else "absent from permitted list (ts_8284206) and fee table (ts_8284213): " + note),
            "fee_rt": F(rt, "USD per round trip", "ts_8284213.html.txt" if rt else None,
                        (f"${rt:.2f}") if rt else None, "commission+NFA+exchange; per side = RT/2"),
            "fee_per_side": F(round(rt / 2, 3) if rt else None, "USD per side", "ts_8284213.html.txt" if rt else None,
                              "Each side (Buy or Sell) incurs half the total" if rt else None, ""),
        }
    return out


def rules():
    return {
        "position_limit_50k": F("Combine 5 minis/50 micros; XFA 2/3/5 by balance; 10:1", None, "ts_8284197.html.txt", "Micros and minis count at a 10:1 ratio."),
        "volatility_caps_50k": F({"CL": 3, "QM": 3, "RB": 3, "HO": 3, "MCL": 30, "GC": 3, "MGC": 30, "SI": 0, "SIL": 2, "HG": 0, "MHG": 2, "PL": 0}, "contracts",
                                 "ts_13613539.html.txt", "Crude Oil (CL) = 3/6/9 ... Micro Crude Oil (MCL) = 30/60/90 ... Silver (SI) = 0 ... Micro Silver (SIL) = 2/5/7 ... Copper (HG) = 0",
                                 "Combine/XFA/Pro column; temporary, no end date"),
        "tier1_news": F("no new opens on ES,RTY,YM,NQ,NKD,GC,SI,HG,PL 5 min before to 5 min after CPI, FOMC decision, FOMC presser, NFP, PPI; micros capped (3 at 50K Combine); energies, rates, FX unaffected", None,
                        "ts_13613539.html.txt", "No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after). ... Other products (energies, rates, FX, etc.) are unaffected."),
        "flat_by": F("15:10", "CT", "ts_8284206.html.txt", "All positions must be closed by 3:10 PM CT every weekday."),
        "grain_hours": F("19:00-07:45 and 08:30-13:20 CT", None, "ts_8284206.html.txt", "Sunday–Monday: 7:00 PM – 7:45 AM CT ... Monday–Friday: 8:30 AM – 1:20 PM CT"),
        "holiday_rule": F("flat 15 min before early close", None, "ts_13350348.html.txt", "All account types must close positions 15 minutes before any early close."),
        "automation_combine": F("allowed with conditions", None, "ts_8284197.html.txt", "Yes, with conditions. Topstep won't help set up or troubleshoot automated strategies"),
        "automation_xfa": F("allowed with conditions", None, "ts_8284215.html.txt", "Yes, with conditions. Topstep won't help set them up or cover malfunctions."),
        "api_bots": F("allowed via TopstepX/ProjectX API; HFT prohibited; not on LFA", None, "ts_11187768.html.txt",
                      "Custom automated strategies and bots are allowed via the TopstepX / ProjectX API, subject to standard platform rules and our prohibition on highfrequency trading (HFT)."),
        "api_cost": F(14.5, "USD/month", "ts_11187768.html.txt", "that's $14.50/month, valid every month with no end date"),
        "api_rate_limit": F("200 requests / 60 s (bars 50 / 30 s)", None, "px_rate_limits.html.txt", "All other Endpoints | 200 requests / 60 seconds"),
        "api_brackets": F(True, None, "px_order_place.html.txt", "Auto OCO Brackets. Brackets attach to each order."),
        "vps": F("prohibited for order transmission", None, "ts_11187768.html.txt",
                 "All trading activity must originate from your personal device. The use of VPS, VPNs, and remote servers is prohibited by Topstep's Terms of Use."),
        "terms_short_term_hft": F("Terms cite short-term or HF trades as an example of prohibited manipulation", None, "ts_terms_of_use.html.txt",
                                  "for example, by engaging in any short term or high frequency trades or simultaneously entering into opposite positions;"),
        "sim_fill_exploitation": F("prohibited", None, "ts_10305426.html.txt",
                                   "Running scalping algorithms designed to exploit unrealistic SIM fills ... Making hundreds of rapid trades to take advantage of preferential queue position in SIM ... usually hundreds or thousands of trades per day, with average durations measured in seconds, not minutes."),
        "outside_bbo": F("prohibited (undefined scope)", None, "ts_10305426.html.txt", "Placing orders at prices outside the current best bid or offer."),
        "min_hold_or_rate_rule": F(None, None, None, None, "No numeric minimum hold or order-rate rule found on today's pages"),
        "platforms": F(["TopstepX", "Quantower via TopstepX (Combine/XFA)", "ProjectX API"], None, "ts_8284179.html.txt",
                       "Quantower via TopstepX is available for the Trading Combine® and Express Funded Account® (XFA) only."),
        "sim_limit_fill_rule": F("trade-through (not touch); partial fills", None, "ts_8765442.html.txt",
                                 "the market has to trade through your price — not just touch it. You might not get filled. Partial fills happen."),
        "data_servers": F("Northern Virginia", None, "ts_14434175.html.txt", "Data servers sit in Northern Virginia"),
    }


def reliability():
    return {
        "founded": F("2010 (Patak Trading Partners); Topstep Trader launched 2012", None, "ts_www_about-us.html.txt", "Founding of Patak Trading Partners ... Launch of Topstep Trader"),
        "paid_out_claim": F("USD 1.5B+ (home) / 1.4B+ (instant payouts page)", None, "ts_www_home.html.txt", "Paid out to prop firm traders1", "instant-payouts page shows $1.4B+; firm claims"),
        "approval_rate_claim": F(0.9926, None, "ts_www_instant-payouts.html.txt", "Payout approval rate", "value shown '99.26%'; firm claim"),
        "stats_2025": F({"combine_pass": 0.168, "participants_funded": 0.518, "funded_paid": 0.333, "xfa_called_up": 0.0071}, None, "ts_www_about-us.html.txt",
                        "16.8% of all Trading Combines initiated were successfully completed"),
        "regulatory_actions": F("none found", None, None, None, "3 WebSearch calls; NFA BASIC unreadable by curl; negative search result only"),
        "nfa_registration_news": F("NFA member, Swap Firm, CTA (Apr-May 2026) [secondary press]", None, "tradeinformer_topstep_cta.html.txt",
                                   "Prop trading firm Topstep has registered with the National Futures Association (NFA) as a Swap Firm and has also been approved to operate as a Commodity Trading Advisor (CTA)."),
        "litigation": F("McCrudden v. Topstepfunded LLC, M.D. Fla. 3:26-cv-00816, filed 2026-04-09, open", None, "cl_docket_mccrudden.html.txt",
                        "COMPLAINT against All Defendants (Filing fee $405.00, receipt number 38733) filed by Vincent McCrudden."),
        "outages_late_2025": F("reported TopstepX outages [pointer]", None, "wiki_topstep.html.txt",
                               "In late 2025, Topstep, experienced a series of critical technical failures on its proprietary trading platform, TopstepX."),
        "change_payout_cap": F("Oct 2025: $5,000 or 50% all sizes -> now 50K Standard $2,000", None, "wb2025_ts_8284233.html.txt",
                               "Traders can request a payout of up to $5,000 or 50% of their account balance after accumulating five winning trading days per payout request."),
        "change_consistency": F("Sep 2025: best day below 50% -> now 55% no buffer", None, "wb2025_ts_8284197.html.txt", "Consistency Target: Best Day below 50% of total profits made"),
        "change_platforms": F("Sep 2025 named NinjaTrader, Quantower, Tradovate, TradingView -> now TopstepX only (+Quantower via TopstepX)", None, "wb2025_ts_8284197.html.txt",
                              "All other trading platforms, including, but not limited to, NinjaTrader, Quantower, Tradovate, and TradingView"),
        "change_b2f_window": F("7 -> 30 days on 2026-05-29", None, "ts_12060405.html.txt", "On May 29th, 2026, the Reactivation window increased from 7 days to 30 days!"),
        "change_wise": F("Wise restored for Canada Aug 2026", None, "ts_8284233.html.txt", "Wise is available again as a payout method for traders in China, Canada, and the United Kingdom."),
    }


def eligibility():
    return {
        "canada_bc_accepted": F(True, None, "ts_8284116.html.txt", "Yes. You trade on a sub-account of Topstep's master account, considered a US-based account.",
                                "Canada not in XFA-only or ineligible lists; no province named"),
        "payout_methods_canada": F(["Wise (no Topstep fee, 1-3 business days)", "Wire/SWIFT (USD 30, 5-10 business days)"], None, "ts_8284233.html.txt",
                                   "Wise is available again as a payout method for traders in China, Canada, and the United Kingdom."),
        "currency": F(None, None, "ts_8284233.html.txt", "supports local currency conversion", "payout currency not stated"),
        "kyc": F("ID + selfie before second purchase; W-8BEN", None, "ts_12578731.html.txt", "It's required before your second purchase and takes only minutes to complete."),
    }


def norm(s):
    s = s.replace("|", " ").replace("​", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def verify(obj, bad, n):
    if isinstance(obj, dict) and "quote" in obj and "source_file" in obj:
        q, sf = obj["quote"], obj["source_file"]
        if q and sf and not sf.endswith(".png"):
            text = norm((REPO / sf).read_text(encoding="utf-8", errors="replace"))
            for frag in [x for x in q.split(" ... ") if x.strip()]:
                n[0] += 1
                if norm(frag) not in text:
                    bad.append((sf, frag))
        return
    if isinstance(obj, dict):
        for v in obj.values():
            verify(v, bad, n)


def main():
    doc = {
        "schema": "e28-A2-firm-1", "firm": "Topstep", "as_of": "2026-10-21", "root": "A2_topstep",
        "fetch_log": PG + "log.tsv",
        "plan_50k": plan(), "funded_stage": funded(), "products": products(), "rules": rules(),
        "reliability": reliability(), "eligibility": eligibility(),
        "e19_diff": {"tsv": "reports/stage_e28_briefs/work/A2_topstep/A2_topstep_e19diff.tsv",
                     "summary": "243 quotes found, 2 flagged and resolved as non-substantive, 31 not checkable (image/unsourced); no recorded value contradicted; gaps listed in the .md section 8"},
    }
    bad, n = [], [0]
    verify(doc, bad, n)
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    print("fragments checked", n[0], "failed", len(bad))
    for sf, frag in bad:
        print("FAIL", sf.split("/")[-1], "|", frag[:150])


if __name__ == "__main__":
    main()
