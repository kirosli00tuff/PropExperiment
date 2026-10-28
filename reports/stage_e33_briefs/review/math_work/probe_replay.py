"""Timing probe: one ZM day through mbo_book31.Book (own replay loop)."""
import os, sys, time
os.nice(10)
sys.path.insert(0, "reports/stage_e33_briefs/work/pipeline")
import numpy as np
import data33, cal33
import mbo_book31 as mb
D = "2022-09-29"
t0 = time.time()
zm = data33.load_zm(D)
fr = cal33.fronts(D)
print("fronts", fr, "n_all", len(zm), "load s", round(time.time()-t0, 2))
iid = fr["ZM"]
sel = zm[zm["instrument_id"] == iid]
print("n_front", len(sel), "n_F_LAST", int(((sel["flags"] & mb.F_LAST) != 0).sum()),
      "acts", {chr(a): int(c) for a, c in zip(*np.unique(sel["action"], return_counts=True))})
t0 = time.time()
book = mb.Book()
n_upd = 0
for r in sel:
    a = int(r["action"]); 
    if a == mb.ACT_CLEAR: book.clear(bool(r["flags"] & mb.F_SNAPSHOT))
    elif a == mb.ACT_ADD: book.add(int(r["order_id"]), mb.book_side(int(r["side"])), int(r["price"]), int(r["size"]))
    elif a == mb.ACT_CANCEL: book.cancel(int(r["order_id"]), int(r["size"]))
    elif a == mb.ACT_MODIFY: book.modify(int(r["order_id"]), mb.book_side(int(r["side"])), int(r["price"]), int(r["size"]))
    elif a == mb.ACT_FILL: book.on_fill(int(r["order_id"]), int(r["size"]))
    if r["flags"] & mb.F_MAYBE_BAD_BOOK: book.mark_bad()
    if r["flags"] & mb.F_LAST:
        n_upd += 1
        if book.in_snapshot: book.end_snapshot()
print("replay s", round(time.time()-t0, 2), "updates", n_upd, "valid_end", book.is_valid(), "best", book.best(0), book.best(1), "anom", book.anomalies)
