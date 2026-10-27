"""M6 (E.32): a simplified, self-written 50K funnel for the worked example of topic (c).

NOT the program's E.19/E.28 simulator (prop_econ/, A3_funnel.py); it was not run or imported. Rules are the
E.28 A3_econ section 3 mappings, simplified as listed in RULES below. No market data is read.

Per-trade model (stated assumption): T trades a day, one position at a time, n contracts, net P&L per trade
normal(mu_net, sig_T^2) ticks, independent; daily P&L normal(m, s^2), m = n T mu_net v, s = n sqrt(T) sig_T v.
Intraday path: Brownian bridge to the close; minimum w = (x - sqrt(x^2 + 2 s^2 E1)) / 2 (E.19's formula);
for intraday-high trailing (Bulenox) the maximum h = (x + sqrt(x^2 + 2 s^2 E2)) / 2, high taken before the low.
Soft DLL first (if DLL < distance to floor and w <= -DLL: day closes at -DLL), else breach if B + w <= floor.
Run: nice -n 10 python3 M6_funnel.py  -> M6_funnel_out.json and a compact table on stdout.
"""
import json
import math
import os

import numpy as np

V = 10.0                     # USD per ZM tick
SIG_T = 3.15 * math.sqrt(15) # ticks per 15-min trade (random-walk scaling assumption)
T_TRADES = 6
NPATH = 20_000
MAX_DAYS = 756
SEED = 20261027
MONTH = 21

RULES = {
    # mll: trailing amount; lock: floor cap (relative to start, None = no lock); dll: soft daily loss limit
    # target: eval profit target; min_days; horizon: eval trading-day limit (None = none);
    # fees: first purchase, purchase after an eval fail, purchase after a funded breach, activation,
    #       monthly rebill in eval (per 21 trading days), API per 21 trading days (whole campaign)
    "topstep": dict(trail="eod", mll=2000, lock_eval=0.0, lock_fund=0.0, dll=None, target=3000, min_days=2,
                    consist_eval=0.55, horizon=None, fee_first=49, fee_reset=49, fee_new=49, act=149,
                    rebill=49, api=14.50, payout="topstep"),
    "lucid": dict(trail="eod", mll=2000, lock_eval=100.0, lock_fund=100.0, dll=1200, target=3000, min_days=1,
                  consist_eval=None, horizon=None, fee_first=172, fee_reset=120, fee_new=172, act=0,
                  rebill=0, api=0, payout="lucid"),
    "tradeify": dict(trail="eod", mll=2000, lock_eval=None, lock_fund=100.0, dll=1250, target=3000, min_days=1,
                     consist_eval=None, horizon=None, fee_first=145, fee_reset=95, fee_new=145, act=0,
                     rebill=0, api=0, payout="tradeify"),
    "mffu": dict(trail="eod", mll=2000, lock_eval=100.0, lock_fund=100.0, dll=1000, target=3000, min_days=2,
                 consist_eval=None, horizon=None, fee_first=153, fee_reset=153, fee_new=153, act=0,
                 rebill=0, api=0, payout="mffu"),
    "bulenox": dict(trail="intraday", mll=2500, lock_eval=100.0, lock_fund=100.0, dll=None, target=3000,
                    min_days=1, consist_eval=None, horizon=21, fee_first=175, fee_reset=175, fee_new=175,
                    act=148, rebill=0, api=100.0, payout="bulenox"),
}


def payout_ok(firm, B, days, wins150, best):
    """First-payout eligibility in the funded stage (balance B relative to start; window = whole funded life)."""
    if firm == "topstep":   # Standard path: 5 winning days of 150+, payout 50% of balance >= 125
        return (wins150 >= 5) & (0.5 * B >= 125)
    if firm == "lucid":     # 3 traded days, balance >= 2,100 buffer + 500, best day <= 40% of window profit
        return (days >= 3) & (B >= 2600) & (best <= 0.40 * B)
    if firm == "tradeify":  # balance >= 3,000, 5 days > 150, best day < 35% of window profit
        return (B >= 3000) & (wins150 >= 5) & (best < 0.35 * B)
    if firm == "mffu":      # >= 2 traded days, balance >= 2,600, best day <= 50% of profit
        return (days >= 2) & (B >= 2600) & (best <= 0.50 * B)
    if firm == "bulenox":   # 10 trading days, balance >= 2,600 reserve + 1,000 min, best day <= 40% cumulative
        return (days >= 10) & (B >= 3600) & (best <= 0.40 * B)
    raise ValueError(firm)


def run(firm, mu_net, n, seed=SEED):
    r = RULES[firm]
    rng = np.random.default_rng(seed)
    m = n * T_TRADES * mu_net * V
    s = n * math.sqrt(T_TRADES) * SIG_T * V
    N = NPATH
    phase = np.zeros(N, np.int8)          # 0 eval, 1 funded, 2 paid, 3 censored
    B = np.zeros(N); peak = np.zeros(N); floor = np.full(N, -float(r["mll"]))
    d_ph = np.zeros(N, np.int32); best = np.zeros(N); wins = np.zeros(N, np.int32)
    attempts = np.ones(N, np.int32); fees = np.full(N, float(r["fee_first"]))
    t_pay = np.full(N, -1, np.int32); pay_amt = np.zeros(N)
    # first-attempt diagnostics (eval month 1 and funded month 1 of the first funded account)
    first_eval = np.ones(N, bool); dll_m1 = np.zeros(N, bool); breach_m1 = np.zeros(N, bool)
    pass_first = np.zeros(N, bool); days_to_pass_first = np.full(N, -1, np.int32)
    first_fund = np.zeros(N, bool); fund_seen = np.zeros(N, bool)
    breach_f_m1 = np.zeros(N, bool); dll_f_m1 = np.zeros(N, bool); paid_first_fund = np.zeros(N, bool)
    breach_f_any = np.zeros(N, bool)
    eval_days_since_bill = np.zeros(N, np.int32)
    for day in range(MAX_DAYS):
        act = phase <= 1
        if not act.any():
            break
        z = rng.standard_normal(N); e1 = -np.log1p(-rng.random(N)); e2 = -np.log1p(-rng.random(N))
        x = m + s * z
        w = (x - np.sqrt(x * x + 2 * s * s * e1)) / 2
        lock = np.where(phase == 0, np.inf if r["lock_eval"] is None else r["lock_eval"], r["lock_fund"])
        if r["trail"] == "intraday":
            h = (x + np.sqrt(x * x + 2 * s * s * e2)) / 2
            floor_day = np.maximum(floor, np.minimum(B + h - r["mll"], lock))   # high before the low
        else:
            floor_day = floor
        d_open = B - floor_day
        close = x.copy()
        dll_hit = np.zeros(N, bool)
        if r["dll"] is not None:
            dll_hit = act & (w <= -r["dll"]) & (r["dll"] < d_open)
            close[dll_hit] = -r["dll"]
        breach = act & ~dll_hit & (w <= -d_open)
        close[breach] = -d_open[breach]
        # diagnostics: first eval attempt, first 21 trading days
        in_m1 = first_eval & (phase == 0) & (d_ph < MONTH)
        dll_m1 |= in_m1 & dll_hit; breach_m1 |= in_m1 & breach
        in_fm1 = first_fund & (phase == 1) & (d_ph < MONTH)
        dll_f_m1 |= in_fm1 & dll_hit; breach_f_m1 |= in_fm1 & breach
        breach_f_any |= first_fund & (phase == 1) & breach
        # update
        B = np.where(act, B + close, B)
        d_ph = np.where(act, d_ph + 1, d_ph)
        best = np.where(act, np.maximum(best, close), best)
        wins = np.where(act & (close >= 150), wins + 1, wins)
        peak = np.where(act, np.maximum(peak, B), peak)
        if r["trail"] == "intraday":
            floor = np.where(act, np.maximum(floor_day, np.minimum(peak - r["mll"], lock)), floor)
        else:
            floor = np.where(act, np.maximum(floor, np.minimum(peak - r["mll"], lock)), floor)
        # fees accruing with time
        fees += r["api"] / MONTH * act   # API pro rata per trading day (approximation of per-started-period)
        ev = act & (phase == 0)
        eval_days_since_bill = np.where(ev, eval_days_since_bill + 1, eval_days_since_bill)
        rb = ev & (eval_days_since_bill >= MONTH) & ~breach
        fees += r["rebill"] * rb
        eval_days_since_bill[rb] = 0
        # evaluation outcomes
        tgt = r["target"] if r["consist_eval"] is None else np.maximum(r["target"], best / r["consist_eval"])
        passed = ev & ~breach & (B >= tgt) & (d_ph >= r["min_days"])
        timeout = ev & ~breach & ~passed & (r["horizon"] is not None) & (d_ph >= (r["horizon"] or 10 ** 9))
        failed = ev & (breach | timeout)
        pass_first |= first_eval & passed
        days_to_pass_first = np.where(first_eval & passed, d_ph, days_to_pass_first)
        first_eval &= ~(passed | failed)
        # funded outcomes
        fu = act & (phase == 1)
        ok = fu & ~breach & payout_ok(firm, B, d_ph, wins, best)
        paid_first_fund |= first_fund & ok
        t_pay = np.where(ok, day + 1, t_pay)
        if firm == "topstep":
            amt = np.minimum(0.5 * B, 2000)
        elif firm == "lucid" or firm == "mffu":
            amt = np.minimum(B - 2100, 2000)
        elif firm == "tradeify":
            amt = np.minimum(B - 100, 1500)
        else:
            amt = np.minimum(B - 2600, 1500)
        pay_amt = np.where(ok, amt, pay_amt)
        fbreach = fu & breach
        first_fund &= ~(ok | fbreach)
        # transitions
        phase = np.where(ok, 2, phase)
        to_fund = passed
        fees += r["act"] * to_fund
        fund_seen_new = to_fund & ~fund_seen
        first_fund |= fund_seen_new; fund_seen |= to_fund
        restart = failed | fbreach
        attempts += restart
        fees += np.where(failed, r["fee_reset"], 0.0) + np.where(fbreach, r["fee_new"], 0.0)
        reset_mask = to_fund | restart
        phase = np.where(to_fund, 1, np.where(restart, 0, phase))
        B[reset_mask] = 0; peak[reset_mask] = 0; floor[reset_mask] = -float(r["mll"])
        d_ph[reset_mask] = 0; best[reset_mask] = 0; wins[reset_mask] = 0
        eval_days_since_bill[reset_mask] = 0
    paid = phase == 2
    res = dict(firm=firm, mu_net=mu_net, n=n, m_day=m, s_day=s,
               p_dll_eval_m1=float(dll_m1.mean()), p_breach_eval_m1=float(breach_m1.mean()),
               p_pass_first_attempt=float(pass_first.mean()),
               median_days_to_pass_first=float(np.median(days_to_pass_first[pass_first])) if pass_first.any() else None,
               p_breach_fund_m1=float(breach_f_m1[fund_seen].mean()) if fund_seen.any() else None,
               p_dll_fund_m1=float(dll_f_m1[fund_seen].mean()) if fund_seen.any() else None,
               p_first_payout_first_funded=float(paid_first_fund[fund_seen].mean()) if fund_seen.any() else None,
               p_paid_within_756=float(paid.mean()),
               mean_days_to_first_payout=float(t_pay[paid].mean()) if paid.any() else None,
               median_days_to_first_payout=float(np.median(t_pay[paid])) if paid.any() else None,
               mean_attempts_paid=float(attempts[paid].mean()) if paid.any() else None,
               mean_fees_to_first_payout=float(fees[paid].mean()) if paid.any() else None,
               mean_first_payout_gross=float(pay_amt[paid].mean()) if paid.any() else None)
    return res


def closed_forms(mu_net, n):
    """Checks: per-day DLL-touch probability of a drifted BM, and Landriault-Li-Zhang (2014) quantities."""
    m = n * T_TRADES * mu_net * V
    s = n * math.sqrt(T_TRADES) * SIG_T * V
    Phi = lambda u: 0.5 * (1 + math.erf(u / math.sqrt(2)))
    out = {}
    for a in (1000, 1200, 1250):
        p = Phi((-a - m) / s) + math.exp(-2 * m * a / s ** 2) * Phi((-a + m) / s) if m != 0 else 2 * Phi(-a / s)
        out[f"p_dll_day_{a}"] = p
        out[f"p_dll_month_{a}"] = 1 - (1 - p) ** MONTH
    for a in (2000, 2500):
        if m > 0:
            g = 2 * m / s ** 2
            out[f"E_tau_dd_{a}_days"] = (s ** 2 * math.exp(g * a) - s ** 2 - 2 * m * a) / (2 * m ** 2)
            out[f"P_reach_3000_before_dd_{a}"] = math.exp(-g * 3000 / (math.exp(g * a) - 1))
        else:
            out[f"E_tau_dd_{a}_days"] = a ** 2 / s ** 2
            out[f"P_reach_3000_before_dd_{a}"] = math.exp(-3000 / a)
    return out


def check_continuous(mu_net, n, a=2500, x_tgt=3000, steps=48, N=20_000, seed=7):
    """Fine-step MC of a continuous trailing drawdown (no lock, no horizon) vs the closed form."""
    rng = np.random.default_rng(seed)
    m = n * T_TRADES * mu_net * V / steps
    s = n * math.sqrt(T_TRADES) * SIG_T * V / math.sqrt(steps)
    X = np.zeros(N); M = np.zeros(N); alive = np.ones(N, bool); win = np.zeros(N, bool)
    tdd = np.zeros(N)
    for k in range(2000 * steps):
        X = X + alive * (m + s * rng.standard_normal(N))
        M = np.maximum(M, X)
        dd = alive & (M - X >= a)
        tdd[dd] = (k + 1) / steps
        hit = alive & ~dd & (M >= x_tgt)
        win |= hit & ~win
        alive &= ~dd
        if not (alive & ~win).any():
            break
    return dict(P_reach_before_dd=float(win.mean()), steps_per_day=steps, N=N)


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    out = {"params": dict(V=V, SIG_T=SIG_T, T=T_TRADES, NPATH=NPATH, MAX_DAYS=MAX_DAYS, SEED=SEED)}
    rows = []
    for mu in (0.0, 0.5, 1.0, 2.0):
        for n in (1, 2, 4):
            for firm in RULES:
                rows.append(run(firm, mu, n))
    out["rows"] = rows
    out["closed"] = {f"{mu}_{n}": closed_forms(mu, n) for mu in (0.0, 0.5, 1.0, 2.0) for n in (1, 2, 4)}
    out["check_continuous_mu1_n1"] = check_continuous(1.0, 1)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "M6_funnel_out.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for r in rows:
        print("%-8s mu=%.1f n=%d dllM1=%.4f brM1=%.3f pass1=%.3f d2p=%s brFM1=%s payFirstF=%s paid=%.3f "
              "Tpay=%s med=%s att=%s fees=%s amt=%s" % (
                  r["firm"], r["mu_net"], r["n"], r["p_dll_eval_m1"], r["p_breach_eval_m1"],
                  r["p_pass_first_attempt"], r["median_days_to_pass_first"],
                  None if r["p_breach_fund_m1"] is None else round(r["p_breach_fund_m1"], 3),
                  None if r["p_first_payout_first_funded"] is None else round(r["p_first_payout_first_funded"], 3),
                  r["p_paid_within_756"],
                  None if r["mean_days_to_first_payout"] is None else round(r["mean_days_to_first_payout"], 1),
                  r["median_days_to_first_payout"],
                  None if r["mean_attempts_paid"] is None else round(r["mean_attempts_paid"], 2),
                  None if r["mean_fees_to_first_payout"] is None else round(r["mean_fees_to_first_payout"], 0),
                  None if r["mean_first_payout_gross"] is None else round(r["mean_first_payout_gross"], 0)))
    print("closed mu1 n1:", {k: round(v, 5) for k, v in out["closed"]["1.0_1"].items()})
    print("check_continuous mu1 n1:", out["check_continuous_mu1_n1"])


if __name__ == "__main__":
    main()
