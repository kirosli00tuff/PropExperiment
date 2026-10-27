"""Binomial pass probabilities for P4.2's rules and the fit/time arithmetic used in the review."""
from math import comb
def p_ge(n, k, p): return sum(comb(n, j) * p**j * (1-p)**(n-j) for j in range(k, n+1))
for p in (0.492, 0.8, 0.914, 0.195):
    print(f"P(>=14 of 20 | p={p}) = {p_ge(20,14,p):.3f}")
print(f"P(>=2 of 20 | 0.05) = {p_ge(20,2,0.05):.3f}; P(>=1 of 20 | 0.05) = {p_ge(20,1,0.05):.3f}; P(>=1 of 10 | 0.05) = {p_ge(10,1,0.05):.3f}")
print(f"P(>=7 of 10 | 0.8) = {p_ge(10,7,0.8):.3f}; P(>=7 of 10 | 0.914) = {p_ge(10,7,0.914):.3f}")
# fits
real = 300*6; print("real search fits", real, "LOGIT", 180*6, "LGBM", 120*6)
for name, s_logit, s_lgbm, thr in (("probe2 (balanced, standardised)", 3.0, 9.0, 5), ("probe1 (99% class 0)", 19.8, 12.0, 8)):
    cpu_logit = 1080*s_logit/3600; thread_h_lgbm = 720*s_lgbm*thr/3600
    print(f"{name}: LOGIT {cpu_logit:.2f} CPU-h; LGBM {720*s_lgbm/3600:.2f} h at {thr} threads = {thread_h_lgbm:.1f} thread-h; wall under 8-thread cap ~ {(cpu_logit + thread_h_lgbm)/8:.2f} h")
syn = 40*real; print("synthetic proofs as written: 40 searches x 1800 =", syn, "fits =", syn/real, "x the search")
print("record generation per replicate at measured rates: ZM.v.0 414.4M + ZS 248.2M + ZL 158.0M = %.1f M records; x40 = %.1f G" % ((414.4+248.2+158.0), 40*(414.4+248.2+158.0)/1000))
print("book+features at 0.5 M rec/s pure python, ZM only: %.1f CPU-h per replicate, x40 = %.0f CPU-h" % (414.4e6/0.5e6/3600, 40*414.4e6/0.5e6/3600))
red = 20*6; print("reduced grid 20 configs x 6 folds =", red, "fits per search; 40 searches =", 40*red, "=", 40*red/real, "x the search")
print("SFI refits: 5 configs x 59 features x 6 folds =", 5*59*6)
print("rows FH15: 263 x 744 =", 263*744, "; training fold ~", round((263*744 - 88*48)*5/6 - 20*263))
