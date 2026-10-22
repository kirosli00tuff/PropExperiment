"""C2_Control: where does the GLFT closed-form bid distance at q=0 cross 1.0 tick (rounding from touch to 1 tick behind)?"""
import math
from scipy.optimize import brentq
def d0(A, k, g, s):
    c1 = (1/g)*math.log(1+g/k); c2 = math.sqrt(s*s*g/(2*k*A)*(1+g/k)**(1+k/g)); return c1 + 0.5*s*c2
for A, k, s in ((0.5, 1.5, 1.0), (0.5, 1.5, 0.5), (0.1, 1.5, 1.0), (0.5, 3.0, 1.0)):
    try:
        gs = brentq(lambda g: d0(A, k, g, s) - 1.0, 1e-6, 50)
        print(f"A={A} k={k} sigma={s}: delta*(q=0) at gamma->0 = {d0(A,k,1e-6,s):.3f}; crosses 1.0 tick at gamma={gs:.4f}")
    except ValueError:
        print(f"A={A} k={k} sigma={s}: delta*(q=0) at gamma->0 = {d0(A,k,1e-6,s):.3f}; no crossing in (1e-6,50)")
