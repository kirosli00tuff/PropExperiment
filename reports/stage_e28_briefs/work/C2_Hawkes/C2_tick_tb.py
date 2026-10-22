import traceback, numpy as np
from tick.hawkes import HawkesExpKern
ts=[np.sort(np.random.default_rng(0).uniform(0,1000,2000)).astype(float)]
try:
    HawkesExpKern(decays=1.0).fit(ts)
    print("fit ok")
except Exception:
    traceback.print_exc()
