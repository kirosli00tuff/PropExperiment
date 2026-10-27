"""MathReview D: independent recomputation of every number in M4_models.md.
No market data. Calendar arithmetic and closed forms only. Prints results only."""
import math
import datetime as dt

SQ2PI = math.sqrt(2 / math.pi)
SIG1 = 3.15
C_E28 = 1.59      # E.28 mu*_mkt (cycle-EV threshold at T=20/day)
C_RT = 1.0 + 0.528  # per-round-trip spread + Topstep fee

def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

print("== M4 section 0: sigma_h, E|r|, p* under 'sign independent of |r|' model, edge at p=0.55 ==")
print("h  sigma_h  E|r|  p*(C=1.59)  p*(C=1.528)  edge@0.55  | location-shift p*=Phi(C/sigma): C=1.59, 1.528")
for h in (1, 5, 15, 30, 60):
    s = SIG1 * math.sqrt(h)
    er = s * SQ2PI
    print(f"{h:3d} {s:7.3f} {er:7.3f} {0.5 + C_E28/(2*er):.4f} {0.5 + C_RT/(2*er):.4f} {0.10*er:.3f} | {Phi(C_E28/s):.4f} {Phi(C_RT/s):.4f}")
print("ratio of edge per unit excess hit rate, location-shift / sign-indep =", (math.sqrt(2*math.pi)/2) / SQ2PI, "(= pi/2)")
print("h=15 check: 1.59/(2*9.734) =", 1.59 / (2 * 9.734))

print("\n== a.3 ==")
z, lam, al = 0.04, 0.02, 0.5
st = math.copysign(max(abs(z) - lam * al, 0), z)
print("EN step:", st / (1 + lam * (1 - al)), " lasso:", z - lam, " ridge:", z / (1 + lam))
print("Platt f=0.8,A=-2,B=0.1:", 1 / (1 + math.exp(-(-2 * 0.8 + 0.1))))
print("calib item3: true", (2*0.56-1)*9.734 - 1.59, " believed", 0.20*9.734 - 1.59)
print("6-month block days:", 816*6/39, " 15-min labels:", 126*19, " 60-min:", 126*4)
print("  with 278-min usable span (M3 g.3): 126*18 =", 126*18, " 60-min 126*4 =", 126*4)

print("\n== b.3 ==")
print("20/15 =", 20/15, " 30*15 =", 30*15, " 30*60 =", 30*60)
print("0.6*816*290 =", 0.6*816*290, " /8 =", 0.6*816*290/8)
print("0.6*15504 =", 0.6*15504, " 2400/9302 =", 2400/9302)
print("leaf w* lam=1: ", 0.6/(3+1), " lam=10:", 0.6/(3+10))

print("\n== c.3 ==")
L, k = 6, 3
R = 1 + 2*(k-1)*(2**L - 1)
print("TCN receptive field:", R, "steps; 10-s grid minutes:", R*10/60)
# parameter counts for the probe architectures (reconstruction from the stated sizes)
tcn = (30*32*3+32) + (32*32*3+32) + (30*32+32) + 5*2*(32*32*3+32) + (32+1)
tr_layer = 4*(64*64+64) + (64*256+256) + (256*64+64) + 2*(2*64)
tr = (30*64+64) + 2*tr_layer + 128*64 + (64+1)
print("TCN params (30->32 ch, 6 blocks, k=3, 1x1 downsample in block 1, linear head):", tcn)
print("Transformer params (d=64, d_ff=256, 2 layers, learned pos emb T=128, input proj, head):", tr)
labels = {1: 236640, 5: 47328, 15: 15504, 60: 3264}
for name, P in (("TCN", 38081), ("DeepLOB", 60947), ("Transformer", 110209)):
    print(name, [round(P/labels[h], 2) for h in (1, 5, 15, 60)])
print("30/15504 =", 30/15504)
print("IC floors: 3/sqrt(15504) =", 3/math.sqrt(15504), " 3/sqrt(9302) =", 3/math.sqrt(9302))

print("\n== c.6 / f.3 compute arithmetic ==")
for rows, thr in ((236640, 18018), (236640, 4466), (5165280, 18018), (5165280, 4466)):
    sec = rows/thr
    print(f"rows {rows} thr {thr}: {sec:.2f} s/epoch; 40 epochs {40*sec/3600:.2f} h")
print("TCN grid 100 fits x 40 x 13.13 s =", 100*40*13.13/3600, "h; 10-s rows", 100*40*286.7/3600, "h")
print("Transformer 100 x 40 x 52.99 =", 100*40*52.99/3600, "h")
print("LightGBM 60 x 26.3 s =", 60*26.3/60, "min")
print("MS: 4.5 x 0.86088/1.87 =", 4.5*0.86088/1.87, "min; x50 =", 50*4.5*0.86088/1.87, "min")
print("saga 300 x 10.6 s =", 300*10.6/60, "min; memory 1M x 30 x 4 =", 1e6*30*4/1e6, "MB; 5M:", 5e6*30*4/1e6, "MB; binned:", 5e6*30/1e6, "MB")
print("860,880 x 30 x 4 =", 860880*30*4/1e6, "MB; 5,165,280 x 30 x 4 =", 5165280*30*4/1e6, "MB")

print("\n== d.3 ==")
th, P, lam, x, y = 0.02, 50.0, 0.99, 1.5, 0.8
kg = P*x/(lam + x*P*x)
e = y - x*th
th1 = th + kg*e
P1 = (P - kg*x*P)/lam
print(f"k={kg:.5f} e={e:.3f} theta={th1:.5f} P={P1:.5f} y/x={y/x:.3f}")
for lam in (0.99, 0.999, 0.9999):
    print(f"lambda {lam}: window {1/(1-lam):.0f} rows = {1/(1-lam)/290:.2f} sessions")
print("1000/15 =", 1000/15, " 1/sqrt(67) =", 1/math.sqrt(67), " ratio to 0.024:", (1/math.sqrt(67))/0.0241)
print("regime stay p11=0.98:", 1/(1-0.98), " p11=0.9993:", 1/(1-0.9993), "min =", 1/(1-0.9993)/290, "sessions")
print("lambda for 20 sessions:", 1 - 1/(20*290))

print("\n== e.3 calendar ==")
d0, d1 = dt.date(2020, 12, 1), dt.date(2024, 2, 29)
wk = sum(1 for i in range((d1-d0).days+1) if (d0+dt.timedelta(i)).weekday() < 5)
print("weekdays 2020-12-01..2024-02-29:", wk, " minus 32 =", wk-32)
hol = ["2020-12-25", "2021-01-01", "2021-01-18", "2021-02-15", "2021-04-02", "2021-05-31", "2021-07-05", "2021-09-06",
       "2021-11-25", "2021-12-24", "2022-01-17", "2022-02-21", "2022-04-15", "2022-05-30", "2022-06-20", "2022-07-04",
       "2022-09-05", "2022-11-24", "2022-12-26", "2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07", "2023-05-29",
       "2023-06-19", "2023-07-04", "2023-09-04", "2023-11-23", "2023-12-25", "2024-01-01", "2024-01-15", "2024-02-19"]
print("my independent CBOT full-closure list count:", len(hol), "(2021-12-31 NOT a closure; all weekdays:",
      all(dt.date.fromisoformat(h).weekday() < 5 for h in hol), ")")

print("\n== e.3 table: non-overlapping labels; 290/765-min base and 278-min usable day span (M3 g.3) ==")
D = 816
print("h  day290 ovn765 dayTot ovnTot both IC_day IC_both | day278 dayTot278 IC_day278")
for h in (1, 5, 15, 30, 60, 120, 240):
    nd, no, nd2 = 290//h, 765//h, 278//h
    Nd, No, Nd2 = nd*D, no*D, nd2*D
    print(f"{h:3d} {nd:4d} {no:4d} {Nd:7d} {No:7d} {Nd+No:7d} {3/math.sqrt(Nd):.4f} {3/math.sqrt(Nd+No):.4f} | {nd2:4d} {Nd2:7d} {3/math.sqrt(Nd2):.4f}")
print("overnight usable span per g.3 (19:05-07:44) = ", (7*60+44) - (19*60+5) + 24*60, "min")
print("per-fold: 0.6/0.2 of 15504:", 0.6*15504, 0.2*15504, " of 3264:", 0.6*3264, 0.2*3264, " of 816:", 0.6*816, 0.2*816)
print("3/sqrt(653) =", 3/math.sqrt(653), " sqrt(0.012) =", math.sqrt(0.012))
print("with 278 span, 60% fold labels: 15-min", 0.6*18*816, " 60-min", 0.6*4*816)

print("\n== e.4 q table (n = 9302 / 1958 / 490) ==")
for name, kk in (("logit30", 31), ("logit60", 61), ("gbm300", 2400), ("gbm100", 800), ("MS", 66), ("TCN", 38081), ("DeepLOB", 60947), ("Transf", 110209)):
    print(f"{name:8s} {kk/9302:.4f} {kk/1958:.3f} {kk/490:.3f}")
print("RLS 30/67 =", 30/67)
print("with 278-span counts (n = 0.6*14688 = 8813): gbm300", 2400/8813, " logit30", 31/8813)
print("e.6: sqrt(15) =", math.sqrt(15))
