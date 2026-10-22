"""C2 worked-example arithmetic (toy numbers, no market data)."""
from math import ceil
TICK=0.25; TV=1.25; FEE_RT=1.22
print("fee RT in ticks:", FEE_RT/TV)
# 1. DeepLOB label, k=5, toy MES mids (illustrative, not data)
past=[4700.00,4700.125,4700.125,4700.25,4700.25,4700.375]  # p_{t-5}..p_t
fut=[4700.375,4700.50,4700.625,4700.625,4700.75]           # p_{t+1}..p_{t+5}
k=5; pt=past[-1]
m_minus_printed=sum(past)/k          # paper as printed: (1/k) sum_{i=0}^{k} -> k+1 terms
m_minus_mean=sum(past[1:])/k         # mean of k most recent incl p_t (i=0..k-1)
m_plus=sum(fut)/k
print("m- printed=%.5f  m- (i=0..k-1)=%.5f  m+=%.5f"%(m_minus_printed,m_minus_mean,m_plus))
l3=(m_plus-pt)/pt; l4=(m_plus-m_minus_mean)/m_minus_mean
print("l_t eq3=%.3e (%.3f bp)  eq4=%.3e (%.3f bp)"%(l3,l3*1e4,l4,l4*1e4))
for a in [0.25e-4,1e-4,2e-3]:
    print(" alpha=%.2e: eq3 label=%d eq4 label=%d"%(a,(l3>a)-(l3<-a),(l4>a)-(l4<-a)))
# 2. threshold conversions
for P in [4700,5000]:
    tb=TICK/P*1e4
    print("MES at %d: 1 tick = %.3f bp; FI-2010 0.002 = %.1f ticks; LSE alpha 0.10..3.05bp = %.2f..%.2f ticks"%(P,tb,0.002*P/TICK,0.10/tb,3.05/tb))
# 3. expected P&L per trade given outcome probs
def ev(pu,ps,pd,g,l,c): return pu*g-pd*l-c
for (pu,ps,pd,g,l) in [(0.60,0.25,0.15,1.5,1.5),(0.60,0.25,0.15,3,3),(0.45,0.35,0.20,2,2)]:
    print("pu=%.2f ps=%.2f pd=%.2f g=l=%.1f: EV mid-mid gross=%.3f ticks, net of fee=%.3f, net of fee+1 tick spread=%.3f"%(pu,ps,pd,g,ev(pu,ps,pd,g,l,0),ev(pu,ps,pd,g,l,FEE_RT/TV),ev(pu,ps,pd,g,l,FEE_RT/TV+1)))
# break-even precision for two-outcome case
c=FEE_RT/TV
for g in [1,2,4]:
    print("g=l=%d ticks: break-even hit rate (fee only)=%.3f ; fee+1tick=%.3f"%(g,(g+c)/(2*g),(g+c+1)/(2*g)))
# 4. sample size: two-group mean difference of markouts, t>3 bar, 80% power
z_a=3.0; z_b=0.8416
for sd,d in [(2,0.25),(2,0.5),(4,0.5),(1,0.25)]:
    n=2*(z_a+z_b)**2*sd**2/d**2
    print("sd=%.1f ticks, delta=%.2f: n per group=%d ; with design effect 3: %d"%(sd,d,ceil(n),ceil(3*n)))
# 5. training time scenarios from probe throughput (samples/s measured)
for name,sps in [("DeepLOB-paper",5247),("DeepLOB-PyTorch32",2092),("TransLOB-like",7725)]:
    for spd,days in [(50000,80),(200000,80)]:
        N=spd*days; ep=N/sps/3600
        print("%s: %d samples/day x %d days = %.1fM/epoch -> %.2f h/epoch, 40 epochs %.1f h"%(name,spd,days,N/1e6,ep,40*ep))
# 6. cloud cost example
for h in [18,100,500]:
    print("GPU-hours %d: RunPod A100 PCIe $1.79 -> $%.0f ; RTX 4090 $0.89 -> $%.0f; Lambda A100 40GB $1.99 -> $%.0f"%(h,1.79*h,0.89*h,1.99*h))
# 7. Briola pT
CT,PT,TT=10,100,100
print("pT example CT=10 PT=100 TT=100 ->", CT/(PT+TT-CT))
# 8. Eurodollar break-even
print("Eurodollar: Sharpe<0 at 12x0.005bp =",12*0.005,"bp vs median spread 0.5 bp -> ratio",0.5/(12*0.005))
