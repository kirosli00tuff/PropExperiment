"""window_for (mine) vs the producer's window_from_end for every midnight-UTC exclusive end, 2024-01-01 to 2027-12-31."""
import importlib.util, datetime as dt
import verify_vol_calc as mine
spec = importlib.util.spec_from_file_location("vm", "../pilot/vol_measure.py")
vm = importlib.util.module_from_spec(spec); spec.loader.exec_module(vm)
d = dt.date(2024, 1, 1); n = bad = 0
while d <= dt.date(2027, 12, 31):
    ns = (d - dt.date(1970, 1, 1)).days * 86_400 * 10**9
    n += 1
    if mine.window_for(d) != vm.window_from_end(ns): bad += 1; print("DIFF", d, mine.window_for(d), vm.window_from_end(ns))
    d += dt.timedelta(days=1)
print("end dates tested", n, "differences", bad)
