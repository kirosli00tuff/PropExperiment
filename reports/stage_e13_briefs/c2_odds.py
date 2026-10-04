"""Lead derivation of C2's odds (Stage E.13 ruling on R-01/R-02). Same structure as the C1 annex section 9:
P(pass) = P(present) x P(pass | present) + (1 - P(present)) x P(pass | absent).
T1 passes iff sample mean >= b (1.5c in sigma units) AND t >= 1.96 AND T1 mean > T2 mean.
mu (true per-trade gross mean, in sigma units, on GEX<0 days) ~ Uniform[lo, hi] when present; 0 when absent.
n = share x 1,913 test dates. SE of the mean = 1/sqrt(n). P(T1 mean > T2 mean | present) = q_cmp."""
from math import sqrt, erf
Phi = lambda x: 0.5 * (1 + erf(x / sqrt(2)))
def p_pass_given_mu(mu, b, n):
    se = 1 / sqrt(n)
    thr = max(b, 1.96 * se)          # both bars on the sample mean
    return 1 - Phi((thr - mu) / se)
def p_pass_present(lo, hi, b, n, q_cmp=0.9, k=400):
    return q_cmp * sum(p_pass_given_mu(lo + (hi - lo) * (i + 0.5) / k, b, n) for i in range(k)) / k
cases = {
    #            P(present) mu_lo mu_hi  b     share  P(persist to 2026+) P(S&P reopened, deployable)
    'skeptical':  (0.25,   0.03, 0.18, 0.17, 0.20,  0.25, 0.8),
    'central':    (0.40,   0.05, 0.25, 0.15, 0.48,  0.35, 0.8),
    'optimistic': (0.55,   0.08, 0.30, 0.13, 0.48,  0.45, 0.9),
}
for name, (pp, lo, hi, b, share, pers, dep) in cases.items():
    n = share * 1913
    ppr = p_pass_present(lo, hi, b, n)
    pa = pp * ppr + (1 - pp) * p_pass_given_mu(0.0, b, n)
    pb = pa * pers * dep
    print(f"{name:10s} n={n:5.0f} P(pass|present)={ppr:.3f} (a)={pa:.3f} (b)={pb:.3f}")
# sensitivity of (a) to P(present) and b at the central mu range and share 0.48
for pp in (0.25, 0.40, 0.55):
    row = []
    for b in (0.13, 0.15, 0.17):
        n = 0.48 * 1913
        row.append(f"b={b}: {pp * p_pass_present(0.05, 0.25, b, n):.3f}")
    print('P(present)', pp, ' '.join(row))
# share sensitivity at central
for share in (0.10, 0.20, 0.30, 0.48):
    n = share * 1913
    print('share', share, 'central (a)=%.3f' % (0.40 * p_pass_present(0.05, 0.25, 0.15, n)))
# C1 for comparison (annex section 9 cases): central 0.22*0.61+0.78*0.04, skeptical 0.12*0.30+0.88*0.04
print('C1 central (a)=%.3f skeptical (a)=%.3f; (b) central %.3f skeptical %.3f' % (
    0.22*0.61+0.78*0.04, 0.12*0.30+0.88*0.04, 0.165*0.8*0.5, 0.071*0.5*0.5))
