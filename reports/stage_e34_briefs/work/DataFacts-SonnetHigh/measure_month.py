"""Decode one ZL MBP-1 month file (guarded) and report record count only; modes: full (whole month in memory) or chunk (1M records)."""
import os, sys, time
from pathlib import Path
os.nice(10)
sys.path.insert(0, str(Path(__file__).parent))
import guard34, databento as db
name, mode = sys.argv[1], sys.argv[2]
p = guard34.check(guard34.MBP1_DIR / name)
store = db.DBNStore.from_file(p)
t = time.time(); n = 0
if mode == "full":
    a = store.to_ndarray(); n = len(a); nbytes = a.nbytes
else:
    nbytes = 0
    for c in store.to_ndarray(count=1_000_000): n += len(c); nbytes = max(nbytes, c.nbytes)
print(mode, name, "records", n, "array_bytes", nbytes, "seconds", round(time.time() - t, 2))
