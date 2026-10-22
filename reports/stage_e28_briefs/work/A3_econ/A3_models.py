"""A3 firm models: each firm's standard 50K plan mapped onto E.19's funnel (FirmModel), with the mapping log.

Plan choice follows the spec rule (the first 50K evaluation plan on the firm's pricing page, as the A2 readers
identified it): Topstep 50K Trading Combine, Standard Path; LucidPro 50K (DLL-on version, the listed price);
Tradeify Growth 50K; MFFU Builder 50K Default; Bulenox Qualification 50K, Option 1 (trailing, listed first).
Topstep's rules come from the E.26-refreshed record (reports/stage_e19_rules.json, headline readings); the other
firms' values come from their A2 records (A2_firm_<firm>.json / .md), cited per rule in MAPPING.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from prop_econ.assemble import FeeTerms, billing_period_days, fee_terms
from prop_econ.grid import headline_book, wallet_from
from prop_econ.rules import CombineRules, SizeRules, size_rules

from A3_funnel import ATTEMPT_CAP, HORIZON, FirmModel, FundedRules

REPO = Path(__file__).resolve().parents[4]
RULES_PATH = REPO / "reports" / "stage_e19_rules.json"
NO_REBILL = 10**9  # one-time fees: a billing period that never elapses


# Every rule of every firm and how the model carries it: (rule, firm value, model form, kind)
# kind: "exact" (represented as stated), "conservative" (not representable or unclear; the stricter or cheaper-
# to-the-firm form used), "ignored" (no effect on a 20 round-trip, size-1, 1-minute-hold strategy), "policy".
MAPPING: dict[str, list[tuple[str, str, str, str]]] = {
    "topstep": [
        ("plan", "50K Trading Combine, Standard Path, USD 49/month (A2 1.1)", "E.19 headline rules, 50K",
         "exact"),
        ("evaluation", "target 3,000; MLL 2,000 EOD trailing, intraday check, locks at start; best day < 55% of "
         "profit; min 2 days; no time limit", "prop_econ simulate_attempts on the refreshed record", "exact"),
        ("fees", "49/month rebill every 30 days (21 trading days), reset 49, a rebill adds a reset credit, a reset "
         "pushes the rebill, activation 149", "prop_econ fee_terms(standard, DLL off, Back2Funded off)", "exact"),
        ("funded", "XFA: start 0, MLL 2,000 EOD, lock 0, floor 0 after the first payout; Standard path 5 days of "
         "150+, net > 0 since last, 50% of balance capped 2,000, min 125, 90/10, payout day not counted",
         "prop_econ simulate_xfas (standard path)", "exact"),
        ("DLL", "optional 1,000 at purchase (doubles caps)", "not chosen (the standard plan's default)",
         "policy"),
        ("Back2Funded", "599, up to 2 before the first payout", "off (E.19 headline)", "policy"),
        ("LFA call-up", "discretionary (0.71% of XFA traders in 2025)", "no automatic call-up (E.19 L-rule)",
         "exact"),
        ("API", "ProjectX API USD 14.50/month", "E.19 wallet: per started 21-day period of the cycle",
         "exact"),
        ("XFA scaling 2/3/5 lots, position caps", "volatility caps CL/QM/GC 3, MCL/MGC 30, SI/HG 0",
         "size 1 always fits except caps of 0 (flagged)", "ignored"),
        ("Tier 1 news", "minis: no new opens 5 min either side of CPI/FOMC/NFP/PPI", "not modelled (R criterion)",
         "ignored"),
        ("commission", "per-product table (A2 section 2); conflict: $3.70/lot simulated Combine fee",
         "product table both stages; the 3.70 reading as a sensitivity", "conservative"),
        ("XFA inactivity 30 days, max 5 XFAs", "-", "one account, trades every day", "ignored"),
    ],
    "lucid": [
        ("plan", "LucidPro 50K, USD 172 one-time, DLL-on version (A2 1a)", "start fee 172, no rebills", "exact"),
        ("evaluation", "target 3,000; MLL 2,000 EOD trailing, locks at +100 once above 52,100; DLL 1,200 soft; "
         "no consistency; min 1 day", "simulate_attempts with combine.dll_usd 1,200, floor cap +100",
         "exact"),
        ("breach test", "'If your account balance reached the MLL' (intraday vs EOD not stated)",
         "intraday worst P&L against the floor (E.19 form)", "conservative"),
        ("reset", "USD 120 restarts a failed evaluation", "reset fee 120 after every failure", "policy"),
        ("activation", "none", "0", "exact"),
        ("funded", "start 50,000, MLL 2,000 EOD, locks at 50,100; buffer 52,100; min profit 500 per cycle; best day "
         "<= 40% of cycle profit; 3 days to payout; min 500; max 2,000 then 2,500; 90/10",
         "extension: traded_days 3, window net >= 500, consistency 0.40 window, buffer 2,100, caps 2,000 / "
         "2,500, min 500, frac 1", "exact"),
        ("funded DLL", "1,200 below 52,100, then 60% of peak EOD profit (soft)", "fixed 1,200 throughout",
         "conservative"),
        ("payout count", "Payout 5 is the maximum level; then live review pool (discretionary), sim accounts "
         "close on going live", "funded account ends after the 5th payout; live stage valued at 0",
         "conservative"),
        ("payout day", "not stated", "payout day not counted in the next window", "conservative"),
        ("inactivity 30 days, 5 funded per household", "-", "one account, trades every day", "ignored"),
        ("microscalping", "flag if > 50% of profit from holds <= 5 s", "1-minute holds", "ignored"),
        ("API", "no Lucid API page; no API fee found", "0", "exact"),
    ],
    "tradeify": [
        ("plan", "Growth 50K, USD 145 one-time (A2 1.1-1.2)", "start fee 145, no rebills", "exact"),
        ("evaluation", "target 3,000; MLL 2,000 EOD trailing enforced in real time, no lock; DLL 1,250 soft; no "
         "consistency; min 1 day", "simulate_attempts, floor cap +inf, combine.dll_usd 1,250", "exact"),
        ("reset", "USD 95", "reset fee 95 after every failure", "policy"),
        ("activation", "none", "0", "exact"),
        ("funded", "start 50,000, MLL 2,000 EOD, locks at 50,100 (EOD 52,100 or first request); DLL 1,250; "
         "request needs balance >= 53,000 and 5 days > 150 since last payout; caps 1,500 / 2,000 / 2,500 / "
         "3,000; min 500; stay above 50,100; 90/10", "extension: win > 150 x 5, min balance 3,000, caps as "
         "stated, buffer 100.01, min 500, lock +100", "exact"),
        ("funded consistency", "35% (Consistency Rule article not fetched: wording unverified)",
         "best day < 35% of the window profit (strict)", "conservative"),
        ("live move", "may be moved to Live after any payout (discretionary)", "no automatic move", "exact"),
        ("microscalping", "> 50% of trades and profit from holds > 10 s", "1-minute holds meet it", "ignored"),
        ("flat 16:45 ET, weekly activity, 15 evaluations a month, 5 funded", "-", "-", "ignored"),
        ("payout day", "not stated", "payout day not counted in the next window", "conservative"),
        ("API", "Tradovate API only on live; no API fee found", "0", "exact"),
    ],
    "mffu": [
        ("plan", "Builder 50K Default, USD 153 one-time (A2 1a)", "start fee 153, no rebills", "exact"),
        ("evaluation", "target 3,000; MLL 2,000 EOD trailing, locks at +100; DLL 1,000 soft pause; no "
         "consistency; min 1 day (plan box says min 2)", "simulate_attempts, floor cap +100, DLL 1,000, min 2 "
         "days", "conservative"),
        ("breach test", "'Open equity losses are counted ... at the end of the trading day'",
         "intraday worst P&L (E.19 form, stricter)", "conservative"),
        ("reset", "no reset price found; a failed account needs a new evaluation", "every failure buys a new "
         "evaluation at 153", "conservative"),
        ("activation", "0", "0", "exact"),
        ("funded", "start 0, MLL 2,000 EOD, locks at +100; DLL 1,000; buffer 2,100; first payout >= 500 above "
         "buffer, later >= 500 since last; >= 2 traded days; best day <= 50% of cycle profit; 500..2,000; 80/20",
         "extension: traded_days 2, min balance 2,600, window net >= 500 after the first, consistency 0.50 "
         "window, buffer 2,100, cap 2,000, min 500", "exact"),
        ("floor after payout", "not stated in the Builder guide; older article: MLL resets to $100",
         "floor fixed at +100 at the first payout", "conservative"),
        ("payout count", "max 5 sim payouts, then promotion to live (Blue Row Capital)",
         "funded account ends after the 5th payout; live stage valued at 0", "conservative"),
        ("payout day", "not stated", "not counted in the next window", "conservative"),
        ("inactivity 7 days, 1 Builder sim funded", "-", "one account, trades every day", "ignored"),
        ("API", "no MFFU API documented; no API fee found", "0", "exact"),
    ],
    "bulenox": [
        ("plan", "Qualification 50K, Option 1 (trailing, listed first), USD 175 one-time, 30 days of access "
         "(A2 1.1-1.2)", "start fee 175", "exact"),
        ("evaluation", "target 3,000; drawdown 2,500 trailing intraday on equity incl. open P&L; locks at +100 "
         "(value 52,600); no DLL; no consistency; no minimum days", "extension: floor trails the day's high, "
         "taken to come before the low (conservative ordering); min 1 day", "conservative"),
        ("30-day access", "hard 30-calendar-day clock per purchase; a reset (78) does not extend it",
         "attempt horizon 21 trading days (E.19 30-day conversion); every attempt is a fresh purchase at 175; "
         "the 78 reset is not used", "conservative"),
        ("activation", "148 one-time per Master account", "148 at the pass", "exact"),
        ("pass review", "manual review, queue, 7-day activation link", "Master starts the next trading day",
         "ignored"),
        ("funded (Master)", "drawdown 2,500 intraday trailing, locks at +100; 10 trading days per payout; "
         "reserve 2,600 above start; min 1,000; max 1,500 for payouts 1-3; best day <= 40% of total P&L, "
         "cumulative; weekly processing (request by Fri, paid Wed; days to Wed not counted)",
         "extension: intraday trailing, traded_days 10, buffer 2,600, min 1,000, caps 1,500, cumulative 0.40, "
         "requests at the start of day 0 of each 5-day week, 2 further days not counted", "exact"),
        ("split", "100% of the first 10,000 per trader profile, then 90%", "90% throughout", "conservative"),
        ("after 3 payouts", "transition to a live Funded account at Bulenox's discretion; nothing carries over; "
         "declining closes the Master", "Master ends after the 3rd payout; live stage valued at 0",
         "conservative"),
        ("API", "third-party API / Trader Composite fee USD 100/month", "E.19 wallet: per started 21-day period",
         "exact"),
        ("third-party algorithm review; scalping algorithms banned", "-", "A criterion", "ignored"),
        ("market data", "non-professional free; professional 116/month", "non-professional", "policy"),
    ],
}


def _one_time_terms(price: float, reset: float, activation: float, split: float) -> FeeTerms:
    return FeeTerms(monthly_usd=price, reset_usd=reset, activation_usd=activation, b2f_usd=0.0,
                    period_days=NO_REBILL, rebill_adds_credit=False, reset_pushes_rebill=False,
                    split=split, attempt_cap=ATTEMPT_CAP, b2f_on=False, b2f_max=0,
                    b2f_before_first_only=True)


def _eval_rules(base: SizeRules, *, target: float, mll: float, lock: float, dll: float | None,
                min_days: int, max_minis: int) -> SizeRules:
    comb = CombineRules(profit_target_usd=target, mll_usd=mll, mll_trail="eod", mll_floor_max_rel_usd=lock,
                        dll_usd=dll, dll_option_usd=None, consistency_type="none", consistency_frac=None,
                        min_trading_days=min_days, max_minis=max_minis)
    return replace(base, combine=comb)


def _funded(**kw: object) -> FundedRules:
    base = dict(trail="eod", floor_after_first_payout=None, dll_usd=None, boundary="lower", win_threshold=None,
                win_strict=False, win_days=0, traded_days=0, net_positive_since_last=False, net_min_first=None,
                net_min_later=None, min_balance=None, consistency_frac=None, consistency_scope="window",
                consistency_inclusive=True, request_weekday=None, dead_days_after_payout=0,
                frac_of_balance=1.0, payout_count_limit=None, payout_day_counts=False, start_balance=0.0)
    base.update(kw)
    return FundedRules(**base)  # type: ignore[arg-type]


def topstep_rules() -> tuple[SizeRules, float, int]:
    book = headline_book(RULES_PATH)
    rules = size_rules(book, "50K")
    w = wallet_from(book, rules)
    return rules, w.api_usd, w.period_days


def firm_models() -> dict[str, FirmModel]:
    ts, api, period = topstep_rules()
    period30 = billing_period_days(30)
    models = {
        "topstep": FirmModel(
            firm="topstep", plan="50K Trading Combine, Standard Path (USD 49/month)", eval_rules=ts,
            eval_trail="eod", eval_dll_usd=None, attempt_max_days=HORIZON, xfa_rules=ts, funded=None,
            terms=fee_terms(ts, pricing_path="standard", dll_chosen=False, b2f_on=False,
                            attempt_cap=ATTEMPT_CAP),
            api_monthly_usd=api, api_period_days=period, mll_usd=ts.combine.mll_usd, dll_usd=None),
        "lucid": FirmModel(
            firm="lucid", plan="LucidPro 50K (USD 172 one-time, DLL on)",
            eval_rules=_eval_rules(ts, target=3000.0, mll=2000.0, lock=100.0, dll=1200.0, min_days=1,
                                   max_minis=4),
            eval_trail="eod", eval_dll_usd=1200.0, attempt_max_days=HORIZON, xfa_rules=None,
            funded=_funded(mll_usd=2000.0, lock_usd=100.0, dll_usd=1200.0, tiers=((None, 4),),
                           traded_days=3, net_min_first=500.0, net_min_later=500.0, consistency_frac=0.40,
                           caps=(2000.0, 2500.0), buffer_usd=2100.0, min_request_usd=500.0,
                           payout_count_limit=5),
            terms=_one_time_terms(172.0, 120.0, 0.0, 0.9), api_monthly_usd=0.0, api_period_days=period30,
            mll_usd=2000.0, dll_usd=1200.0),
        "tradeify": FirmModel(
            firm="tradeify", plan="Growth 50K (USD 145 one-time)",
            eval_rules=_eval_rules(ts, target=3000.0, mll=2000.0, lock=1e12, dll=1250.0, min_days=1,
                                   max_minis=4),
            eval_trail="eod", eval_dll_usd=1250.0, attempt_max_days=HORIZON, xfa_rules=None,
            funded=_funded(mll_usd=2000.0, lock_usd=100.0, dll_usd=1250.0, tiers=((None, 4),),
                           win_threshold=150.0, win_strict=True, win_days=5, min_balance=3000.0,
                           consistency_frac=0.35, consistency_inclusive=False,
                           caps=(1500.0, 2000.0, 2500.0, 3000.0), buffer_usd=100.01, min_request_usd=500.0),
            terms=_one_time_terms(145.0, 95.0, 0.0, 0.9), api_monthly_usd=0.0, api_period_days=period30,
            mll_usd=2000.0, dll_usd=1250.0),
        "mffu": FirmModel(
            firm="mffu", plan="Builder 50K Default (USD 153 one-time)",
            eval_rules=_eval_rules(ts, target=3000.0, mll=2000.0, lock=100.0, dll=1000.0, min_days=2,
                                   max_minis=4),
            eval_trail="eod", eval_dll_usd=1000.0, attempt_max_days=HORIZON, xfa_rules=None,
            funded=_funded(mll_usd=2000.0, lock_usd=100.0, floor_after_first_payout=100.0, dll_usd=1000.0,
                           tiers=((None, 4),), traded_days=2, min_balance=2600.0, net_min_later=500.0,
                           consistency_frac=0.50, caps=(2000.0,), buffer_usd=2100.0, min_request_usd=500.0,
                           payout_count_limit=5),
            terms=_one_time_terms(153.0, 153.0, 0.0, 0.8), api_monthly_usd=0.0, api_period_days=period30,
            mll_usd=2000.0, dll_usd=1000.0),
        "bulenox": FirmModel(
            firm="bulenox", plan="Qualification 50K, Option 1 trailing (USD 175 one-time, 30 days)",
            eval_rules=_eval_rules(ts, target=3000.0, mll=2500.0, lock=100.0, dll=None, min_days=1,
                                   max_minis=7),
            eval_trail="intraday", eval_dll_usd=None, attempt_max_days=period30, xfa_rules=None,
            funded=_funded(mll_usd=2500.0, trail="intraday", lock_usd=100.0, tiers=((None, 7),),
                           traded_days=10, consistency_frac=0.40, consistency_scope="cumulative",
                           request_weekday=0, dead_days_after_payout=2, caps=(1500.0,), buffer_usd=2600.0,
                           min_request_usd=1000.0, payout_count_limit=3),
            terms=_one_time_terms(175.0, 175.0, 148.0, 0.9), api_monthly_usd=100.0, api_period_days=period30,
            mll_usd=2500.0, dll_usd=None),
    }
    return models
