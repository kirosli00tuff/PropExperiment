"""Stage E.19 lead: condensed rule table (key rules per size, value, status, source) from reports/stage_e19_rules.json.
Prints markdown for the return's section 3."""
import json

d = json.load(open("reports/stage_e19_rules.json"))
st = {r["path"]: r for r in d["rules"]}
ROWS = [("Combine monthly price, Standard / No Activation Fee pricing", "combine.monthly_price_usd.standard", "combine.monthly_price_usd.no_activation_fee"),
        ("Reset price, Standard / NAF", "combine.reset_price_usd.standard", "combine.reset_price_usd.no_activation_fee"),
        ("Profit target", "combine.profit_target_usd", None),
        ("Combine MLL (EOD trailing; locks at start balance)", "combine.mll_usd", "combine.mll_floor_max_rel_usd"),
        ("Combine consistency: best day max share of total profit", "combine.consistency.frac", None),
        ("Minimum trading days", "combine.min_trading_days", None),
        ("Max position (minis)", "combine.max_minis", None),
        ("Optional DLL (both phases, chosen at purchase)", "combine.dll_option_usd", None),
        ("Activation fee, Standard / NAF", "activation_fee_usd.standard", "activation_fee_usd.no_activation_fee"),
        ("XFA MLL (EOD trailing, locks at $0) / after the 1st payout", "xfa.mll_usd", "xfa.mll_after_first_payout_usd"),
        ("Standard path: winning days x minimum", "xfa.payout.standard.winning_days", "xfa.payout.standard.winning_day_usd"),
        ("Standard path cap / with DLL", "xfa.payout.standard.cap_usd", "xfa.payout.standard.cap_usd_dll"),
        ("Consistency path: days / best-day max share", "xfa.payout.consistency.traded_days", "xfa.payout.consistency.best_day_max_frac"),
        ("Consistency path cap / with DLL", "xfa.payout.consistency.cap_usd", "xfa.payout.consistency.cap_usd_dll"),
        ("Payout max share of balance", "xfa.payout.standard.frac_of_balance", None),
        ("Back2Funded price / max per XFA", "xfa.back2funded.price_usd", "xfa.back2funded.max_per_xfa"),
        ("Scaling plan first tier (minis) / boundary reading", "xfa.scaling.0.max_minis", "xfa.scaling_boundary")]
G = [("Profit split to trader", "global.profit_split_trader"), ("Minimum payout", "global.payout_min_request_usd"),
     ("Max active XFAs", "global.max_active_xfas"), ("Billing period (calendar days)", "global.billing_period_calendar_days"),
     ("Rebill adds a reset credit", "global.rebill_adds_reset_credit"), ("Live Funded call-up", "global.callup.type"),
     ("Automated trading allowed (Combine, XFA)", "global.automated_trading_allowed"), ("VPS allowed", "global.vps_allowed"),
     ("Cross-account hedging allowed", "global.cross_account_hedging_allowed"), ("API access per month", "global.api_access_monthly_usd")]


def cell(path):
    r = st[path]
    tag = "" if r["status"] == "SOURCED" else f" ({r['status']})"
    return f"{r['value']}{tag} [{r['source']}]"


print("| Rule | 50K | 100K | 150K |\n|---|---|---|---|")
for name, a, b in ROWS:
    cells = []
    for s in ("50K", "100K", "150K"):
        x = cell(f"sizes.{s}.{a}")
        if b:
            x += " / " + cell(f"sizes.{s}.{b}")
        cells.append(x)
    print(f"| {name} | " + " | ".join(cells) + " |")
print("\n| Rule (all sizes) | Value |\n|---|---|")
for name, p in G:
    print(f"| {name} | {cell(p)} |")
