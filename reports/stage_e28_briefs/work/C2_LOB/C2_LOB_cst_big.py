import sys; sys.path.insert(0,'.')
from C2_LOB_cst_cdl import cst_exec_before_move, cst_mid_up
lam, mu, th = 1.85, 0.94, 0.71
for b in [1,2,5,10,20]:
    print(b, [round(cst_exec_before_move(a,b,lam,mu,th,N=120),3) for a in (1,5,10,20)])
