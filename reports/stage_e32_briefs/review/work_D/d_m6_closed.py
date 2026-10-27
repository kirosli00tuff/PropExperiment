"""MathReview D: closed-form recomputation of M6_prop_strategy.md sections 1, 2 (hand check), 3, 4, 5.
No market data. Prints results only."""
import math

def Phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

SIG1 = 3.15
s5, s15, s60 = SIG1 * math.sqrt(5), SIG1 * math.sqrt(15), SIG1 * math.sqrt(60)
FEES = {"Topstep": 0.528, "Lucid": 0.560, "Lucid_u": 0.920, "Tradeify": 0.920, "MFFU": 0.612, "Bulenox": 0.572}

print("== sec 0: sigma_h ==", round(s5, 3), round(s15, 3), round(s60, 3), " check 12.2^2/15 =", 12.2**2/15)
print("== 1.3 item 1-2: p* = Phi(c/sigma) ==")
for f, F in FEES.items():
    c = 1.0 + F
    print(f"{f:9s} c={c:.3f} p5={Phi(c/s5):.4f} p15={Phi(c/s15):.4f} p60={Phi(c/s60):.4f} pu*(b=10)={0.5 + c/20:.4f}")
c = 1.528
print("Taylor check Phi(0.12525):", 0.5 + 0.39894*(0.12525 - 0.12525**3/6), " exact:", Phi(c/s15))
print("item 3: net", 2.0 - c, "ticks =", (2.0-c)*10, "USD; x6 =", (2.0-c)*60, "USD; Phi(2/12.2) =", Phi(2.0/s15))
# item 4: two-sided barrier with drift
mu = 2.0/15; var = SIG1**2; gam = 2*mu/var
a = l = 10
pu = (1 - math.exp(gam*l)) / (math.exp(-gam*a) - math.exp(gam*l))
pu_alt = 1/(1 + math.exp(-gam*a))
Enet = (2*pu - 1)*a - c
Etau = (pu*a - (1-pu)*l)/mu
print(f"item 4: gamma={gam:.6f} e^+={math.exp(gam*a):.5f} e^-={math.exp(-gam*a):.5f} P(+10 first)={pu:.4f} (alt form {pu_alt:.4f}) "
      f"E[net]={Enet:.3f} E[X_tau]={(2*pu-1)*a:.3f} E[tau]={Etau:.2f} min; driftless a*l/sigma^2={a*l/var:.2f}")

print("\n== 2.3 hand check: first passage to -1 within 1 min, mu=0.1333/min, sigma=3.15 ==")
d, t = 1.0, 1.0
p_cont = Phi((-d - mu*t)/(SIG1*math.sqrt(t))) + math.exp(-2*mu*d/var)*Phi((-d + mu*t)/(SIG1*math.sqrt(t)))
print("continuous:", round(p_cont, 4))
beta = 0.5826; dtm = 1/60
shift = beta*SIG1*math.sqrt(dtm)
d2 = d + shift
p_bgk = Phi((-d2 - mu*t)/(SIG1*math.sqrt(t))) + math.exp(-2*mu*d2/var)*Phi((-d2 + mu*t)/(SIG1*math.sqrt(t)))
print(f"BGK shift={shift:.4f} level={d2:.4f} corrected p={p_bgk:.4f}")
# numerical integral of the first-passage density as a third check
n = 200000
acc = 0.0
for i in range(1, n+1):
    tt = (i - 0.5)*t/n
    acc += d/(SIG1*math.sqrt(2*math.pi*tt**3))*math.exp(-(d + mu*tt)**2/(2*var*tt))*(t/n)
print("density integral:", round(acc, 4))
print("E[delta_L] at L=1 s:", mu/60, " SD:", SIG1*math.sqrt(1/60), "; L=0.3 s SD:", SIG1*math.sqrt(0.3/60), " mean:", mu*0.3/60)

print("\n== 2.3 identities on the file's own simulated inputs ==")
p, EGF, EGnF, alpha_sim = 0.683, 0.747, 4.798, 2.030
print("decomp:", p*EGF + (1-p)*EGnF)
VM = alpha_sim - 1.528; VL = p*(EGF - 0.528); OC = (1-p)*(EGnF - 1.528)
print(f"V_M={VM:.3f} V_L={VL:.3f} OC={OC:.3f} OC-ps={OC - p*1:.3f} V_M-V_L={VM-VL:.3f}")
print("V_L cal:", p*(EGF - 0.470 - 0.528), " V_LC:", 1.298 - 1.028)
pq, EGFq = 0.807, 1.253
print("Bulenox V_M:", alpha_sim - 1.572, " V_L BM:", pq*(EGFq - 0.572), " K cal:", pq*(EGFq - 0.572 - 0.287), " FIFO cal:", pq*(EGFq - 0.572 - 0.252))
print("queue decomposition 5.5:", 0.807*1.253 + 0.193*5.278)

print("\n== 3.3: C1-C4 ==")
m = 1*6*1.0*10; s = 1*math.sqrt(6)*s15*10; s2 = s*s
print(f"m={m} s={s:.4f} s^2={s2:.1f}")
def Pday(a, m, s):
    return Phi((-a - m)/s) + math.exp(-2*m*a/(s*s))*Phi((-a + m)/s)
for a in (1000, 1200, 1250):
    pd = Pday(a, m, s)
    print(f"a={a}: P_day={pd:.6f} P_month={1-(1-pd)**21:.5f}")
print("item2 pieces:", Phi((-1000-60)/s), math.exp(-2*60*1000/s2), Phi((-1000+60)/s))
def Etau_dd(a, m, s):
    return (s*s*math.exp(2*m*a/(s*s)) - s*s - 2*m*a)/(2*m*m)
for a in (2000, 2500):
    print(f"C3 a={a}: E[tau]={Etau_dd(a, m, s):.1f} days; zero edge {a*a/s2:.1f}")
def Preach(x, a, m, s):
    g = 2*m/(s*s)
    return math.exp(-g*x/(math.exp(g*a) - 1))
for a in (2000, 2500):
    print(f"C4 a={a}: P(+3000 before dd)={Preach(3000, a, m, s):.4f}")
print("gamma:", 2*m/s2, " gamma*3000:", 2*m/s2*3000, " exp(gamma*2000)-1:", math.exp(2*m/s2*2000)-1)

print("\n== 3.3 item 6/7 ==")
m2, sN2 = 120, 2*s
pd2 = Pday(1000, m2, sN2)
print(f"n=2 MFFU: P_day={pd2:.4f} P_month={1-(1-pd2)**21:.3f}")
for a, firm in ((1000, "MFFU"), (1200, "Lucid"), (1250, "Tradeify")):
    print(f"n<= {a}/(3*{s:.2f}) = {a/(3*s):.2f} ({firm})")
s60d = math.sqrt(3)*s60*10
print(f"60-min T=3: s={s60d:.1f}; 1000/s={1000/s60d:.2f} SD; 2Phi(-2.37)={2*Phi(-1000/s60d):.4f}/day -> every {1/(2*Phi(-1000/s60d)):.0f} days")
print("P(x>=150):", Phi((60-150)/s))
print("Bulenox: 21*60 =", 21*60, " s*sqrt(21) =", s*math.sqrt(21), " z =", (3000-1260)/(s*math.sqrt(21)))
for firm, fees, days in (("Topstep", 366, 68.6), ("Lucid", 245, 103.4), ("Tradeify", 212, 111.3), ("MFFU", 232, 103.3), ("Bulenox", 2692, 226.6)):
    print(f"fees/trade {firm}: {fees/(6*days*10):.3f} tick")
print("150/298.84 =", 150/s)
print("5.4b Topstep market: m =", 6*0.527*10, " s =", s)

print("\n== 4.2 price limit ==")
for D in (20, 30):
    print(f"D={D}, P=300: line = {D - 0.02*300} USD/ton = {(D-0.02*300)*10:.0f} ticks")

print("\n== 5.4a derived columns ==")
print("Topstep (ii) cal per trade:", 0.744 - 0.470 - 0.528, " per signal:", 0.684*(0.744-0.470-0.528),
      " chase:", 0.684*(0.744-0.470-0.528) + 0.316*(2.002 - 1 - 0.528))
print("Bulenox K cal per trade:", 1.273 - 0.287 - 0.572, " per signal:", 0.808*(1.273-0.287-0.572))
print("decomp 5.4:", 0.684*0.744 + 0.316*4.895)
print("market alpha* = 1+F; alpha(1.0) = 2+F:")
for f, F in FEES.items():
    print(f"  {f:9s} alpha*={1+F:.3f} p*15={Phi((1+F)/s15):.4f} alpha(1.0)={2+F:.3f} p15(alpha1.0)={Phi((2+F)/s15):.4f}")
for name, al in (("TT L cal", 2.317), ("TT LC cal", 2.080), ("TT L BM", 1.836), ("Lucid K", 1.626), ("Lucid FIFO", 1.590), ("MFFU TT L", 2.403), ("Tradeify TT L", 2.719), ("Bul K", 1.638), ("Bul FIFO", 1.602), ("Bul BM", 1.347)):
    print(f"  p*_15 for alpha*={al}: {Phi(al/s15):.4f}")
print("TT extra over market: ", 2.317-1.528, 2.403-1.612, 2.719-1.920, "; queue extra:", 1.638-1.572, 1.602-1.572, 1.626-1.560, 1.590-1.560)
print("Phi(2.53/12.2) =", Phi(2.53/s15), " Phi(2.92/12.2) =", Phi(2.92/s15))
print("E.28 1.59 decomposed: 1.59 - 1.528 =", 1.59-1.528, "; mu*_lim 0.59 - 0.528 =", 0.59-0.528)
