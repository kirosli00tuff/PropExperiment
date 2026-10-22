"""A3 timing / memory probe: one evaluation per firm on NQ-like and MNQ-like pairs."""
import os, resource, sys, time
import numpy as np
import A3_funnel as F
import A3_models as M

os.nice(10)
t0 = time.time()
models = M.firm_models()
da = F.make_draws("attempt", with_max=True)
dx = F.make_draws("xfa", with_max=True)
print("draws", round(time.time() - t0, 2), "s rss", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, "MB")
att, xfa = F.cycle_indices()
for firm in sys.argv[1].split(","):
    m = models[firm]
    for mu, c, sig, v in [(1.5, 0.756, 27.83, 5.0), (4.0, 2.44, 27.83, 0.5)]:
        law = F.DayLaw.from_trades(mu, c, sig, v)
        t1 = time.time()
        pools = F.simulate_pools(m, law, da, dx)
        t2 = time.time()
        st = F.cycle_stats(m, pools, att, xfa)
        t3 = time.time()
        p = F.campaign_p_reach(m, pools)
        t4 = time.time()
        print(firm, mu, c, "m", round(law.m, 1), "s", round(law.s, 1), "EV", round(st.ev, 1), "se", round(st.se, 1),
              "P10K", round(p, 4), "att", round(st.mean_attempts, 2), "fees/att", round(st.eval_fees_per_attempt, 1),
              "t pools", round(t2 - t1, 2), "cyc", round(t3 - t2, 2), "camp", round(t4 - t3, 2),
              "rss", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, "MB", flush=True)
