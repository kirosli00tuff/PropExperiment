import sys; sys.path.insert(0, '.')
import numpy as np
from C2_LOB_cst_cdl import cst_exec_before_move
lam, mu, th = 1.85, 0.94, 0.71
paper4 = {(1,1): .497, (1,5): .776, (3,1): .206, (5,5): .393, (2,3): .535, (5,1): .118}
# Variant V1: order cancels too? (death mu+j*th) -> emulate via th on all j: implement directly
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
def gen(a,b,deathW,N=80):
    idx=lambda i,j:(i-1)*b+(j-1); A=lil_matrix((N*b,N*b)); r=np.zeros(N*b)
    for i in range(1,N+1):
        for j in range(1,b+1):
            k=idx(i,j); rates=[]
            if i<N: rates.append(((i+1,j),lam))
            rates.append(((i-1,j),mu+i*th)); rates.append(((i,j-1),deathW(j)))
            A[k,k]=sum(q for _,q in rates)
            for (ii,jj),q in rates:
                if jj==0: r[k]+=q
                elif ii==0: pass
                else: A[k,idx(ii,jj)]-=q
    return spsolve(A.tocsr(),r)[idx(a,b)]
for (b,a),pv in paper4.items():
    v0=cst_exec_before_move(a,b,lam,mu,th)
    v2=gen(a,b+1,lambda j: mu+(j-1)*th) if True else None
    v3=gen(a,b,lambda j: mu)  # no cancellations ahead
    print(f"b={b} a={a} paper={pv} base={v0:.3f} b+1={v2:.3f} noCancelAhead={v3:.3f}")
