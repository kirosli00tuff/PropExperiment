import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
lam, mu, th = 1.85, 0.94, 0.71
paper4 = {(1,1): .497, (1,5): .776, (3,1): .206, (5,5): .393, (2,3): .535, (5,1): .118}
def gen(a,b,N=80,ownCancel=True,askDeath=lambda i: mu+i*th):
    idx=lambda i,j:(i-1)*b+(j-1); A=lil_matrix((N*b,N*b)); r=np.zeros(N*b)
    for i in range(1,N+1):
        for j in range(1,b+1):
            k=idx(i,j); rates=[]
            if i<N: rates.append(((i+1,j),lam))
            rates.append(((i-1,j),askDeath(i))); rates.append(((i,j-1),mu+(j-1)*th))
            if ownCancel: rates.append(((-1,-1),th))
            A[k,k]=sum(q for _,q in rates)
            for (ii,jj),q in rates:
                if jj==0: r[k]+=q
                elif ii<=0: pass
                else: A[k,idx(ii,jj)]-=q
    return spsolve(A.tocsr(),r)[idx(a,b)]
for (b,a),pv in paper4.items():
    print(f"b={b} a={a} paper={pv} ownCancelFails={gen(a,b):.3f}")
