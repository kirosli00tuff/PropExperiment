"""MathReview D: own simplified evaluation/funded simulation for M6 sections 3.3 and 5.4b (Topstep and MFFU cells).
Model (mine, stated): daily P&L x ~ N(m, s^2) USD, m = n T mu v, s = n sqrt(T) sigma_T v; intraday minimum by the
Brownian-bridge formula w = (x - sqrt(x^2 + 2 s^2 E1))/2 with E1 ~ Exp(1); 21 trading days a month.
Evaluation: start 0, target 3,000 (pass when EOD balance >= 3,000), EOD-trailing floor = peak(EOD) - 2,000, floor
locked once it reaches +100; breach when balance + w <= floor; optional soft DLL (day closes at -DLL when w <= -DLL).
Funded (after a pass): start 0, same trailing floor and lock; first payout when 5 days of P&L >= 150 and balance >= 250.
After a breach a new evaluation is bought. Fees (Topstep): 49 per started 21-day evaluation period, 14.50 per started
21-day period overall. Prints results only."""
import numpy as np

rng = np.random.default_rng(20261028)
SIG15 = 3.15 * np.sqrt(15)
V = 10.0

def run(mu_net: float, n: int, T: float, dll: float | None, npaths: int = 20000, maxdays: int = 756, lock_at: float = 100.0):
    m = n * T * mu_net * V
    s = n * np.sqrt(T) * SIG15 * V
    X = rng.normal(m, s, size=(npaths, maxdays))
    E1 = rng.exponential(1.0, size=(npaths, maxdays))
    Wmin = (X - np.sqrt(X * X + 2 * s * s * E1)) / 2
    if dll is not None:
        hit = Wmin <= -dll
        X = np.where(hit, -dll, X)
        Wmin = np.where(hit, -dll, Wmin)
    out = dict(dll_m1=0, breach_m1=0, pass1=0, pass_days=[], fund_breach_m1=0, fund_n=0, paid=0, days_paid=[], attempts=[], fees=[], paid_first_funded=0)
    for i in range(npaths):
        day = 0; attempts = 0; eval_periods = 0; paid = False; first_funded = True
        while day < maxdays and not paid:
            # evaluation
            attempts += 1
            bal = 0.0; peak = 0.0; floor = -2000.0; locked = False; d0 = day; passed = False; breached = False
            while day < maxdays:
                x, w = X[i, day], Wmin[i, day]
                if bal + w <= floor:
                    breached = True; day += 1; break
                bal += x; day += 1
                if not locked:
                    peak = max(peak, bal); floor = peak - 2000.0
                    if floor >= lock_at:
                        floor = lock_at; locked = True
                if bal >= 3000.0:
                    passed = True; break
            eval_periods += int(np.ceil(max(day - d0, 1) / 21))
            if attempts == 1:
                if breached and day - d0 <= 21: out["breach_m1"] += 1
                if passed:
                    out["pass1"] += 1; out["pass_days"].append(day - d0)
            if not passed:
                continue
            # funded
            out["fund_n"] += 1 if first_funded else 0
            bal = 0.0; peak = 0.0; floor = -2000.0; locked = False; d1 = day; wins = 0
            while day < maxdays:
                x, w = X[i, day], Wmin[i, day]
                if bal + w <= floor:
                    if first_funded and day - d1 < 21: out["fund_breach_m1"] += 1
                    day += 1; break
                bal += x; day += 1
                if x >= 150: wins += 1
                if not locked:
                    peak = max(peak, bal); floor = peak - 2000.0
                    if floor >= lock_at:
                        floor = lock_at; locked = True
                if wins >= 5 and bal >= 250:
                    paid = True
                    if first_funded: out["paid_first_funded"] += 1
                    break
            first_funded = False
        if paid:
            out["paid"] += 1; out["days_paid"].append(day); out["attempts"].append(attempts)
            out["fees"].append(49 * eval_periods + 14.5 * int(np.ceil(day / 21)))
    # DLL month-1 count: recompute cleanly (first 21 days of the first attempt, any day with w <= -dll)
    if dll is not None:
        out["dll_m1"] = int((Wmin[:, :21] <= -dll).any(axis=1).sum())
    npth = npaths
    return dict(m=m, s=s,
                P_dll_m1=out["dll_m1"] / npth if dll is not None else 0.0,
                P_breach_m1=out["breach_m1"] / npth,
                P_fund_breach_m1=out["fund_breach_m1"] / max(out["fund_n"], 1),
                P_pass1=out["pass1"] / npth,
                med_pass=float(np.median(out["pass_days"])) if out["pass_days"] else float("nan"),
                P_paid_first_funded=out["paid_first_funded"] / max(out["fund_n"], 1),
                P_paid=out["paid"] / npth,
                mean_days=float(np.mean(out["days_paid"])) if out["days_paid"] else float("nan"),
                med_days=float(np.median(out["days_paid"])) if out["days_paid"] else float("nan"),
                attempts=float(np.mean(out["attempts"])) if out["attempts"] else float("nan"),
                fees=float(np.mean(out["fees"])) if out["fees"] else float("nan"))

def show(label, r):
    print(f"{label}: m={r['m']:.1f} s={r['s']:.1f} P(DLL m1)={r['P_dll_m1']:.4f} P(breach m1)={r['P_breach_m1']:.3f} "
          f"P(fund breach m1)={r['P_fund_breach_m1']:.3f} P(pass1)={r['P_pass1']:.3f} med pass={r['med_pass']:.0f} "
          f"P(paid|1st funded)={r['P_paid_first_funded']:.3f} P(paid 756)={r['P_paid']:.3f} days={r['mean_days']:.1f} ({r['med_days']:.0f}) "
          f"attempts={r['attempts']:.2f} fees={r['fees']:.0f}")

show("Topstep mu1.0 n1 T6 (M6: 0.063/0.051/0.810/37/0.930/68.6(59)/1.33/366)", run(1.0, 1, 6, None))
show("MFFU-like DLL1000 mu1.0 n1 T6 (M6 P(DLL m1) 0.0078, breach 0.063, pass 0.806)", run(1.0, 1, 6, 1000.0))
show("MFFU-like DLL1000 mu1.0 n2 (M6 P(DLL) 0.537, pass 0.573)", run(1.0, 2, 6, 1000.0))
show("Topstep mu0.0 n1 (M6 pass 0.253, days 239.1)", run(0.0, 1, 6, None))
show("Topstep mu0.5 n1 (M6 pass 0.562, days 115.7)", run(0.5, 1, 6, None))
show("Topstep mu2.0 n1 (M6 pass 0.979, days 38.0)", run(2.0, 1, 6, None))
show("Topstep mu1.0 n2 (M6 pass 0.580, days 43.9)", run(1.0, 2, 6, None))
show("5.4b Topstep market mu0.527 T6 (M6: breach 0.122, fund 0.106, pass 0.578, paid 1.000, days 111.5, fees 519)", run(0.527, 1, 6, None))
show("5.4b Topstep TT L mu-0.254 T4.10 (M6: breach 0.162, pass 0.136, paid 0.675, days 341.5)", run(-0.254, 1, 4.10, None))
# closed-form comparison for the pass probability without lock/clock: P(+3000 before dd 2000), continuous trailing
m, s = 60.0, np.sqrt(6) * SIG15 * V
g = 2 * m / (s * s)
print("closed-form continuous-trailing P(+3000 before 2000 dd) at mu 1.0 n 1:", round(float(np.exp(-g * 3000 / (np.exp(g * 2000) - 1))), 4))
