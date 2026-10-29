"""Independent recomputation of M4 / L arithmetic (reviewer's own code, no frozen imports).
Pure arithmetic; no market data. Prints a compact table."""
import math
from datetime import date, timedelta
from statistics import NormalDist

Z = NormalDist()
G = 0.5772156649015329


def e_max(n):
    return (1 - G) * Z.inv_cdf(1 - 1 / n) + G * Z.inv_cdf(1 - 1 / (n * math.e))


def dsr(sr, t, n, v, sk=0.0, ku=3.0):
    sr0 = math.sqrt(v) * e_max(n)
    den = math.sqrt(1 - sk * sr + (ku - 1) / 4 * sr * sr)
    return Z.cdf((sr - sr0) * math.sqrt(t - 1) / den)


def se(sr, t, sk=0.0, ku=3.0):
    return math.sqrt((1 - sk * sr + (ku - 1) / 4 * sr * sr) / (t - 1))


def bisect(f, lo=0.0, hi=1.0, it=200):
    for _ in range(it):
        m = (lo + hi) / 2
        if f(m):
            hi = m
        else:
            lo = m
    return hi


def thresholds(n, td, tt, sk=0.0, ku=3.0):
    g3 = bisect(lambda s: dsr(s, td, n, 1 / (td - 1), sk, ku) >= 0.95)
    dsr_t = bisect(lambda s: dsr(s, tt, n, 1 / (tt - 1), sk, ku) >= 0.95)
    b = max(3 / math.sqrt(tt), dsr_t)
    g4 = bisect(lambda s: s - se(s, td, sk, ku) >= b)
    sel = max(g3, g4)
    z80 = Z.inv_cdf(0.8)
    s80_t = b + z80 * se(b, tt, sk, ku)
    # exact alternative: true SR whose 20th percentile of the estimate equals b
    s80_t_exact = bisect(lambda s: s - z80 * se(s, tt, sk, ku) >= b)
    s80_sel = sel + z80 * se(sel, td, sk, ku)
    return dict(e=e_max(n), sr0=math.sqrt(1 / (td - 1)) * e_max(n), g3=g3, b=b, g4=g4, sel=sel,
                s80_t=s80_t, s80_t_exact=s80_t_exact, s80_sel=s80_sel)


def weekdays(a, b):
    n, d = 0, a
    while d <= b:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


print("weekdays disc", weekdays(date(2020, 12, 1), date(2024, 2, 29)),
      "test MBO", weekdays(date(2017, 5, 22), date(2020, 11, 30)),
      "test MBP1", weekdays(date(2017, 5, 1), date(2020, 11, 30)),
      "2017-05-01..19", weekdays(date(2017, 5, 1), date(2017, 5, 19)))
print("z80", round(Z.inv_cdf(0.8), 4), "z95", round(Z.inv_cdf(0.95), 4))
for n, td, tt in ((838, 796, 870), (1038, 796, 870), (1138, 796, 870), (838, 796, 885), (838, 776, 850)):
    r = thresholds(n, td, tt)
    print(f"N{n} Td{td} Tt{tt}: e {r['e']:.4f} SR0 {r['sr0']:.4f} G3 {r['g3']:.4f} b {r['b']:.6f} "
          f"G4 {r['g4']:.4f} sel {r['sel']:.4f} SR80t {r['s80_t']:.4f} (exact {r['s80_t_exact']:.4f}) "
          f"SR80sel {r['s80_sel']:.4f}")
for sk, ku in ((-0.5, 6.0), (0.0, 10.0), (0.0, 20.0), (-2.0, 30.0)):
    r = thresholds(838, 796, 870, sk, ku)
    print(f"moments sk{sk} ku{ku}: sel {r['sel']:.4f} SR80t {r['s80_t']:.4f} "
          f"ratio sel {r['sel']/0.2007:.3f} ratio s80 {r['s80_t']/0.1936:.3f}")
SIG = {15: 20.37, 30: 28.10, 60: 38.21}
for s80, tag in ((0.1936, "N838"), (0.1957, "N1038"), (0.1920, "N838 MBP1")):
    print(tag, "e80 caps 19/9/4:", [round(s80 * SIG[h] / math.sqrt(n), 3) for h, n in ((15, 19), (30, 9), (60, 4))],
          "caps 17/8/4:", [round(s80 * SIG[h] / math.sqrt(n), 3) for h, n in ((15, 17), (30, 8), (60, 4))],
          "h30 n1/2/4/8:", [round(s80 * 28.10 / math.sqrt(n), 3) for n in (1, 2, 4, 8)])
print("K2 item2 n*", round((0.2007 * 20.37 / 1.8) ** 2, 3), "ratio G4/SR80", round(0.2007 / 0.1936, 4),
      "G4 per-trade h30 n1/n2", round(0.2007 * 28.1, 2), round(0.2007 * 28.1 / math.sqrt(2), 2))
print("Holm K9 m1/2/3 z", [round(Z.inv_cdf(1 - 0.05 / 9 / m), 3) for m in (1, 2, 3)], "f", round(4.86 / 2.902, 3))
print("D2 mult 838", round(e_max(838) / 2, 3), round(e_max(838) * math.sqrt(2) / 3, 3))
print("gap SD", round(math.sqrt(se(0.25, 870) ** 2 + se(0.15, 870) ** 2), 4))
print("kurt 3/p at p=0.5", 3 / 0.5)
# L.a
for lab, T in (("quiet", 6998), ("p5", 12352), ("med", 19206)):
    tpm = T * 0.762 / 290
    print(f"L.a {lab}: T/min {tpm:.2f} n5 {tpm*5:.1f} SD {1/math.sqrt(tpm*5):.3f}")
print("L.a book ev/s", round(168917 * 0.703 / 17400, 2), "DF34 F_LAST share", round(142061153 / 158046466, 4),
      "188782x", round(188782 * 142061153 / 158046466))
print("L.b caps", [math.floor((277 - h) / (h + 1)) + 1 for h in (15, 30, 60)],
      "E.32b caps", [min(20, 290 // h) for h in (15, 30, 60)],
      "decision minutes", [278 - h for h in (5, 15, 30, 60)])
print("burn40 ratio", round(0.2031 / 0.2007, 4), round(0.1959 / 0.1936, 4))
print("gross h30 n2/n1", round(2.38 + 3.85, 2), round(2.38 + 5.44, 2), "in sigma30",
      round(6.23 / 28.1, 3), round(7.82 / 28.1, 3))
