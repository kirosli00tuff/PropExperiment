"""Independent recomputation of every number in M1_order_flow.md worked examples.
Standard ZM numbers: tick 10 USD, sigma_1m 3.15 ticks, BE 1.59 ticks, fee 0.528 ticks,
ADV 36,690, day share 0.83, day session 290 min. Prints results only."""
import math
from statistics import NormalDist

N = NormalDist()
SIG1 = 3.15
BE = 1.59
ADV = 36_690
DAY_SHARE = 0.83
DAY_MIN = 290
SQ2PI = math.sqrt(2 / math.pi)


def sig(h: float) -> float:
    return SIG1 * math.sqrt(h)


print("== Section 1: R2 needed")
z90 = N.inv_cdf(0.95)
cond = N.pdf(z90) / 0.05  # E[|Z| : |Z| > z90]
print(f"z90 {z90:.4f}  phi {N.pdf(z90):.5f}  E|Z| top decile {cond:.4f}  sqrt(2/pi) {SQ2PI:.4f}")
for h in (1, 5, 15, 30):
    s = sig(h)
    r2_all = (BE / (s * SQ2PI)) ** 2
    r2_top = (BE / (s * cond)) ** 2
    print(f"h={h:>2} sigma_h {s:.3f}  R2 all {r2_all:.4f}  R2 top decile {r2_top:.4f}")

print("== 2.3 (i) stylized impact")
D = 50
print(f"OFI for 1 tick = 2D = {2*D}; OFI 30 -> dP {30/(2*D):.2f} tick")

print("== 2.3 (ii) R2_pred = rho^2 R2_c")
for rho in (0.05, 0.1, 0.2):
    print(f"rho {rho}: {rho**2*0.65:.4f}")

print("== 2.3 (iii) CRS mapping")
for lab, r2, h in (("1996 5m", 0.0332, 5), ("1996 30m", 0.0053, 30), ("2002 5m", 0.0054, 5), ("2002 30m", 0.0018, 30)):
    s = sig(h)
    sdf = math.sqrt(r2) * s
    print(f"{lab}: sigma_h {s:.3f} sd(f) {sdf:.3f} mean|f| {sdf*SQ2PI:.3f} top-decile {sdf*cond:.3f}")
print(f"R2 ratio 1996 5m/30m {0.0332/0.0053:.2f} vs 1/h ratio {30/5:.1f}; 5-min fall 1996->2002 {0.0332/0.0054:.2f}")

print("== 2.3 (iv) KTW horizon")
changes_per_min = SIG1 ** 2
sec_per_change = 60 / changes_per_min
print(f"changes/min {changes_per_min:.2f}  s per change {sec_per_change:.2f}  two changes {2*sec_per_change:.1f} s")

print("== 2.6 compute")
days = 39 / 12 * 252
msgs = 2e6 * days
print(f"days {days:.0f} msgs {msgs/1e9:.2f}e9  cpu at 5-10M/s {msgs/1e7/60:.1f}-{msgs/5e6/60:.1f} min")
rows = days * 23 * 3600
print(f"per-second rows {rows/1e6:.1f}M  bytes M=5 f32 {rows*5*4/1e9:.2f} GB")

print("== 3.3 (i) BGPW Ne")
C0, gam = 0.2, 0.2
closed = 1 + C0 / (1 - gam) * 1000 ** (1 - gam)
exact = 1 + sum(C0 * l ** (-gam) for l in range(1, 1001))
print(f"closed {closed:.2f} exact {exact:.2f}")

print("== 3.3 (ii) asymmetric liquidity")
eh, th = 0.2, 0.5
rp, rm = th * (1 - eh), th * (1 + eh)
pp = (1 + eh) / 2
print(f"r+ {rp:.2f} r- {rm:.2f} phi+ {pp:.2f} E[dm] {pp*rp - (1-pp)*rm:.4f}")
print(f"alpha=2-2H: H=0.7 -> {2-2*0.7:.1f}")

print("== 4.3 Kyle lambda")
dayvol = ADV * DAY_SHARE
print(f"day vol {dayvol:.1f}  per min {dayvol/DAY_MIN:.1f}")
lam, sdq = 0.02, 60
r2c = (lam * sdq) ** 2 / SIG1 ** 2
print(f"R2_c {r2c:.4f}  forward rho=0.1 {0.01*r2c:.5f}")
for h in (5, 15, 30):
    print(f"slope at {h} min {lam*h**-0.25:.5f}")
print(f"30^-0.25 {30**-0.25:.4f}; Hasbrouck sqrt(1e4)*7e-6 = {math.sqrt(1e4)*7e-6:.4f}")

print("== 5.3 microprice")
I = 40 / 50
print(f"I {I:.2f} adj {I-0.5:+.2f} tick; 0.5/BE {0.5/BE:.2f}")

print("== 6.3 refill toy")
for tau in (2, 20):
    r = 1 - math.exp(-6 / tau)
    print(f"tau {tau}: R(6s) {r:.4f}")
print(f"ratio {(1-math.exp(-3))/(1-math.exp(-0.3)):.2f}")

print("== 7.3 iceberg square root")
sday = sig(DAY_MIN)
extra = sday * (math.sqrt(120 / ADV) - math.sqrt(40 / ADV))
print(f"sigma_day {sday:.2f} sqrt(120/ADV) {math.sqrt(120/ADV):.5f} sqrt(40/ADV) {math.sqrt(40/ADV):.5f} extra {extra:.3f}")
print(f"1000-lot: {sday*math.sqrt(1000/ADV):.2f} ticks; sqrt(1000/ADV) {math.sqrt(1000/ADV):.4f}; vs 96-tick range {sday*math.sqrt(1000/ADV)/96:.2f}")
print(f"BM expected range over 290 min: {math.sqrt(8/math.pi)*sday:.1f} ticks; over 23 h: {math.sqrt(8/math.pi)*sig(23*60):.0f}")

print("== 8.3 VPIN")
V = ADV / 50
imb = [200, 150, 400, 100, 300]
print(f"V {V:.1f}; VPIN {sum(imb)/(5*734):.5f} (V=734) {sum(imb)/(5*V):.5f} (V=733.8)")
print(f"Z(3/3.15) = {N.cdf(3/3.15):.4f}")

print("== 9.1 drift burst")
d_core = 1528
for cnt in (97, 29):
    print(f"{cnt}/{d_core}*819 = {cnt/d_core*819:.1f}")
print(f"15/sigma_5 {15/sig(5):.2f}; -0.2*15 {-0.2*15:.1f}; net {3.0-BE:.2f}; BE/0.2 {BE/0.2:.2f}; BE/0.1 {BE/0.1:.1f}")
print(f"3/sqrt(52) {3/math.sqrt(52):.3f}; sqrt(52) {math.sqrt(52):.2f}; evaluations {819*23*720/1e6:.1f}M")
print(f"power 80% at t=3 needs mean/sd {(3+0.8416)/math.sqrt(52):.3f}")
