"""Independent recomputation of every number in M3_labels.md worked examples.
Standard ZM numbers: sigma_1m 3.15 ticks, BE 1.59, fee 0.528, ADV 36,690, day share 0.83,
day session 290 min, 816 trade dates. Prints results only."""
import math
from statistics import NormalDist

N = NormalDist()
SIG1 = 3.15
BE = 1.59
FEE = 0.528
ADV = 36_690
DAY_MIN = 290
DATES = 816
SQ2PI = math.sqrt(2 / math.pi)


def sig(h: float) -> float:
    return SIG1 * math.sqrt(h)


def p_no_barrier(a: float, s: float, h: float, terms: int = 50) -> float:
    """P(driftless BM with per-minute sd s stays inside (-a, a) up to time h)."""
    tot = 0.0
    for n in range(terms):
        k = 2 * n + 1
        tot += (-1) ** n / k * math.exp(-(k ** 2) * math.pi ** 2 * s ** 2 * h / (8 * a ** 2))
    return 4 / math.pi * tot


def t95(a: float, s: float) -> float:
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if p_no_barrier(a, s, mid) > 0.05:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


print("== A1 check")
print(f"sqrt(8/pi) {math.sqrt(8/math.pi):.4f}; range 290 min {math.sqrt(8/math.pi)*sig(290):.1f} ticks; Roll s^2/2 share {0.5/SIG1**2:.3f}")

print("== a.3 volume bars")
V = ADV / 50
day = ADV * 0.83
night = ADV * 0.17
print(f"V {V:.1f}; day bars {day/V:.2f}; min/bar {DAY_MIN/(day/V):.2f}; at 109.2/min {V/109.2:.2f}")
print(f"night bars {night/V:.2f}; at 8.5/min {V/8.5:.1f} min; at 2/min {V/2:.0f} min; overnight minutes {12*60+45}")

print("== a.3 CUSUM toy H=6")
y = [2, 1, -1, 3, 1, -2, -3, -2, 1, -2, 0, 4]
sp = sn = 0.0
H = 6
ev = []
for i, v in enumerate(y, 1):
    sp = max(0.0, sp + v)
    sn = min(0.0, sn + v)
    if sn < -H:
        sn = 0.0
        ev.append(("neg", i))
    elif sp > H:
        sp = 0.0
        ev.append(("pos", i))
    print(f"t{i}: S+ {sp:g} S- {sn:g}")
print("events", ev)
for H in (6, 10, 12, 15):
    print(f"H {H}: H^2/sigma^2 {H**2/SIG1**2:.2f} min")

print("== b.2 first passage")
for kap in (1, 2):
    print(f"kappa {kap}: P(no barrier by h) {p_no_barrier(kap*SIG1, SIG1, 1):.4f}")
print(f"E[sqrt(290-u)] factor 2/3 -> sd {2/3*sig(290):.2f}; equiv h {(2/3)**2*290:.1f}")

print("== b.3")
for k in (4, 5, 6):
    print(f"k {k}: E[tau] {k**2/SIG1**2:.2f} min; 95% by {t95(k, SIG1):.2f} min; p* mid-barrier {(k+BE)/(2*k):.4f}; p* exec-barrier (cost 0.59) {(k+0.59)/(2*k):.4f}")
print(f"check k=5: {0.659*3.41 - 0.341*6.59:.4f}")
a60 = sig(60)
print(f"a(60,k=1) {a60:.2f}; p* {0.5 + BE/(2*a60):.4f}")
print(f"sigma_15 {sig(15):.2f}; 1/sigma_15 {1/sig(15):.3f}")
print(f"sigma_290 {sig(290):.2f}; sigma_20 {sig(20):.2f}; ratio {sig(290)/sig(20):.3f}; sqrt(14.5) {math.sqrt(14.5):.3f}")
print(f"b.6 starts {DATES*DAY_MIN:,}")

print("== c.3 meta-labeling")
k = sig(15)
pstar = (k + BE) / (2 * k)
print(f"k {k:.2f} p* {pstar:.4f}; spacing {144/SIG1**2:.2f}; events/day {DAY_MIN/(144/SIG1**2):.1f}; total {DATES*20:,}")
nacc, p = 3264, 0.58
net = p * (k - BE) - (1 - p) * (k + BE)
se = math.sqrt(p * (1 - p) / nacc)
print(f"net {net:.3f}; se {se:.5f}; t {(p-pstar)/se:.2f}; n for t=3 {p*(1-p)*(3/(p-pstar))**2:.0f}")
sd = 2 * k * math.sqrt(p * (1 - p))
print(f"total edge {nacc*net:.0f}; per day {nacc*net/DATES:.2f}; sd {sd:.2f}; SR {net/sd:.3f}")

print("== d.3 uniqueness (15-min labels every minute, 290 bars)")
h = 15
labels = list(range(0, DAY_MIN - h + 1))
c = [0] * (DAY_MIN + 1)
for t0 in labels:
    for j in range(t0 + 1, t0 + h + 1):
        c[j] += 1
u = []
for t0 in labels:
    u.append(sum(1 / c[j] for j in range(t0 + 1, t0 + h + 1)) / h)
print(f"labels {len(labels)}; max c {max(c)}; u first {u[0]:.4f} second {u[1]:.4f} third {u[2]:.4f} interior {u[100]:.4f}")
print(f"H_15 {sum(1/i for i in range(1,16)):.4f}; n_eff {sum(u):.4f}; mean u {sum(u)/len(u):.4f}; 816x {sum(u)*DATES:,.0f}; labels x816 {len(labels)*DATES:,}")
print(f"d.6 ops {len(labels)*DATES*h:.2e}; seq {(len(labels)*DATES)**2*h:.2e}; per date {len(labels)**2*h:.3e}; x816 {len(labels)**2*h*DATES:.2e}")
ub = [0.5, 0.5, 1, 1]
x = []
acc = 0
for v in ub:
    acc += v
    x.append(acc)
X = x[-1]
for C in (0.5, -0.25):
    b = (1 - C) / X if C >= 0 else 1 / ((C + 1) * X)
    a = 1 - b * X
    d = [max(0, a + b * xi) for xi in x]
    print(f"C {C}: b {b:.4f} a {a:.4f} d {[round(v,4) for v in d]}")

print("== e.4 latency")
for L in (0.3, 1.0):
    print(f"L {L}s: sd {SIG1*math.sqrt(L/60):.3f} tick")
print(f"fraction 1s/60s {1/60:.3%}; 1s/900s {1/900:.2%}")

print("== e.5")
print(f"2/sigma_15 {2/sig(15):.3f}; net {2-1-FEE:.3f} -> {2-1-FEE-0.062:.3f}; front-loaded {2-1-BE:.2f}")
print(f"Phi(1.528/12.2)-0.5 {N.cdf(1.528/sig(15))-0.5:.4f}; with 1.59: {N.cdf(BE/sig(15))-0.5:.4f}")

print("== f.3 table")
hdr = "h sigma E|dM| BE/sig q* q*(1.528) q*bar1 q*bar2 n t_at_q* q_t3"
print(hdr)
for h in (1, 5, 15, 30, 60, 120, 240, 290):
    s = sig(h)
    e = s * SQ2PI
    q = 0.5 + BE / (2 * e)
    q2 = 0.5 + 1.528 / (2 * e)
    qb1 = 0.5 + BE / (2 * s)
    qb2 = 0.5 + BE / (4 * s)
    n = DATES * (DAY_MIN // h)
    se = 0.5 / math.sqrt(n)
    print(f"{h:>3} {s:7.3f} {e:7.3f} {BE/s:6.3f} {q:.4f} {q2:.4f} {qb1:.4f} {qb2:.4f} {n:>7,} {(q-0.5)/se:6.1f} {q+3*se:.4f}")
s = 2 / 3 * sig(290)
e = s * SQ2PI
print(f"uniform-entry close: sigma {s:.3f} E {e:.3f} BE/sig {BE/s:.3f} q* {0.5+BE/(2*e):.4f} q*(1.528) {0.5+1.528/(2*e):.4f} bar1 {0.5+BE/(2*s):.4f} bar2 {0.5+BE/(4*s):.4f}")
print("dead zone P(|dM|<=1.59):", {h: round(2 * N.cdf(BE / sig(h)) - 1, 3) for h in (5, 15, 60)}, f"Phi(0.2257) {N.cdf(BE/sig(5)):.4f}")
p = 0.68
m = (2 * p - 1) * 5 - BE
sd = 10 * math.sqrt(p * (1 - p))
print(f"item5: mean {m:.2f} sd {sd:.3f} SR {m/sd:.3f}")
print(f"power (80%) q needed at h=60: {0.5 + BE/(2*sig(60)*SQ2PI) + (3+0.8416)*0.5/math.sqrt(3264):.4f}")

print("== g.4")
allowed = DAY_MIN - 5 - 7
print(f"allowed {allowed}; starts {allowed-15+1}; excluded starts {(11*60+30)-(10*60+43)+1}; kept {allowed-14-48}")
b1 = (10 * 60 + 58) - (8 * 60 + 35)
b2 = (13 * 60 + 13) - (11 * 60 + 30)
print(f"blocks {b1} {b2}; n_eff {(b1+b2)/15:.2f} vs {allowed/15:.2f}; ratios {216/264:.3f} {((b1+b2)/15)/(allowed/15):.3f}")
print(f"per year loss {15*(allowed/15-(b1+b2)/15):.1f} of {250*allowed/15:.0f} = {15*(allowed/15-(b1+b2)/15)/(250*allowed/15):.2%}")
