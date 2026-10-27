"""M4 worked-example arithmetic (pure numbers from the brief's standard ZM table; no data read)."""
import math
s1 = 3.15
for h in (1, 5, 15, 30, 60):
    sh = s1 * math.sqrt(h); ea = sh * math.sqrt(2 / math.pi)
    p_need = 0.5 + 1.59 / (2 * ea)
    print(f"h={h}: sigma_h={sh:.3f} ticks, E|r|={ea:.3f}, p_needed(1.59 hurdle)={p_need:.4f}, edge at p=0.55: {(0.1*ea):.3f}")
# Platt
A, B, f = -2.0, 0.1, 0.8
print("platt p =", 1 / (1 + math.exp(A * f + B)))
# enet coordinate update
z, lam, al = 0.04, 0.02, 0.5
st = math.copysign(max(abs(z) - lam * al, 0), z)
print("enet beta =", st, st / (1 + lam * (1 - al)))
# RLS step
th, P, l, x, y = 0.02, 50.0, 0.99, 1.5, 0.8
k = P * x / (l + x * P * x); e = y - x * th
print("rls k", k, "e", e, "theta", th + k * e, "P", (P - k * x * P) / l)
for lam_ in (0.99, 0.999, 0.9999):
    print("lambda", lam_, "h=1/(1-l)", 1 / (1 - lam_), "day sessions at 1-min rows", 1 / (1 - lam_) / 290)
# t=3 IC example
for ic in (0.02, 0.03, 0.05):
    print("IC", ic, "n for t=3:", (3 / ic) ** 2)
# params vs ESS
for name, p in (("DeepLOB", 60947), ("TCN probe", 38081), ("tinyTF probe", 110209)):
    print(name, [round(p / n, 3) for n in (236640, 47328, 15504, 3264)])
# TCN receptive field: 6 levels, k=3, 2 convs per block, dilations 1..32
print("TCN RF", 1 + 2 * (3 - 1) * sum(2 ** i for i in range(6)))
# epochs
print("TCN epoch secs 236640 rows", 236640 / 18018, "5.17M rows", 5165280 / 18018, "40 ep h", 40 * 5165280 / 18018 / 3600)
print("tinyTF epoch secs 236640", 236640 / 4466, "5.17M", 5165280 / 4466, "40 ep h", 40 * 5165280 / 4466 / 3600)
print("10s rows day", 816 * 290 * 6, "both", 816 * 1055 * 6)
print("RLS secs per 1M", 1.639 * 5, "for 860880 rows", 1.639 / 200000 * 860880)
