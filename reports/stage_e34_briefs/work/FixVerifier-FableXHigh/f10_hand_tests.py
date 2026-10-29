"""FixVerifier-FableXHigh: hand tests of the v0.2 F10.7 (QI1s) and F10.9 (CR5 removal count) definitions on
synthetic MBP-1 streams. No market data. Records: (ts, action, side, price, size, bid_px, bid_sz, ask_px, ask_sz, last, bad)."""
import os
os.nice(10)
NONE = None

def updates(recs):
    return [r for r in recs if r['last']]

def qb_tilde_v02(recs, t, side='bid'):
    px = 'bid_px' if side == 'bid' else 'ask_px'; sz = 'bid_sz' if side == 'bid' else 'ask_sz'
    ups = [r for r in updates(recs) if r['ts'] <= t]
    # price-change events between consecutive book updates
    changes = []  # (ts, old, new)
    for a, b in zip(ups, ups[1:]):
        if a[px] != b[px]:
            changes.append((b['ts'], a[px], b[px]))
    recent = [c for c in changes if t - 1.0 < c[0] <= t]
    if recent:
        ts_c, old, new = recent[-1]
        inc = (new > old) if side == 'bid' else (new < old)   # ask: a decrease plays the role of a rise
        if inc:
            return 0, 'zero (most recent change was an improvement)'
    last_change = changes[-1][0] if changes else float('-inf')
    t_c = max(t - 1.0, last_change)
    states = [r for r in ups if t_c <= r['ts'] <= t]
    asof = [r for r in ups if r['ts'] <= t_c]
    cand = [r[sz] for r in states] + ([asof[-1][sz]] if asof else [])
    return min(cand), f'min over [{t_c:.1f}, {t:.1f}]'

def qb_tilde_v01(recs, t, side='bid'):
    px = 'bid_px' if side == 'bid' else 'ask_px'; sz = 'bid_sz' if side == 'bid' else 'ask_sz'
    ups = [r for r in updates(recs) if r['ts'] <= t]
    changes = [(b['ts'], a[px], b[px]) for a, b in zip(ups, ups[1:]) if a[px] != b[px]]
    rose = any((t - 1.0 < c[0] <= t) and ((c[2] > c[1]) if side == 'bid' else (c[2] < c[1])) for c in changes)
    if rose:
        return 0, 'zero (rose at any time in the second)'
    last_change = changes[-1][0] if changes else float('-inf')
    t_c = max(t - 1.0, last_change)
    states = [r for r in ups if t_c <= r['ts'] <= t]
    asof = [r for r in ups if r['ts'] <= t_c]
    return min([r[sz] for r in states] + ([asof[-1][sz]] if asof else [])), 'min'

def batches(recs):
    out, cur = [], []
    for r in recs:
        cur.append(r)
        if r['last']:
            out.append(cur); cur = []
    return out

def cb_v02(recs, side='bid'):
    """Removal count per batch under v0.2: D_b(p) over every consecutive pair of any action, minus T_b(p), floored."""
    px = 'bid_px' if side == 'bid' else 'ask_px'; sz = 'bid_sz' if side == 'bid' else 'ask_sz'
    total, detail = 0, []
    prev_state = None
    for b in batches(recs):
        bad = any(r['bad'] for r in b)
        D, T = {}, {}
        seq = ([prev_state] if prev_state is not None else []) + b
        for a, c in zip(seq, seq[1:]):
            if bad or a[px] is NONE or c[px] is NONE:
                continue
            fell = (c[px] < a[px]) if side == 'bid' else (c[px] > a[px])
            if c[px] == a[px] and c[sz] < a[sz]:
                D[a[px]] = D.get(a[px], 0) + a[sz] - c[sz]
            elif fell:
                D[a[px]] = D.get(a[px], 0) + a[sz]
        for r in b:
            if r['action'] == 'T':
                T[r['price']] = T.get(r['price'], 0) + r['size']
        cb = sum(max(0, D.get(p, 0) - T.get(p, 0)) for p in set(D) | set(T))
        detail.append((dict(D), dict(T), cb)); total += cb
        prev_state = b[-1]
    return total, detail

def cb_v01(recs, side='bid'):
    """v0.1 / M1 form: decreases on C or M records only, less the batch's T lots at that price, floored."""
    px = 'bid_px' if side == 'bid' else 'ask_px'; sz = 'bid_sz' if side == 'bid' else 'ask_sz'
    total = 0; prev_state = None
    for b in batches(recs):
        D, T = {}, {}
        seq = ([prev_state] if prev_state is not None else []) + b
        for a, c in zip(seq, seq[1:]):
            if c['action'] not in ('C', 'M'):
                continue
            if c[px] == a[px] and c[sz] < a[sz]:
                D[a[px]] = D.get(a[px], 0) + a[sz] - c[sz]
            elif c[px] < a[px]:
                D[a[px]] = D.get(a[px], 0) + a[sz]
        for r in b:
            if r['action'] == 'T':
                T[r['price']] = T.get(r['price'], 0) + r['size']
        total += sum(max(0, D.get(p, 0) - T.get(p, 0)) for p in set(D) | set(T))
        prev_state = b[-1]
    return total

def R(ts, action, side, price, size, bpx, bsz, apx, asz, last=True, bad=False):
    return dict(ts=ts, action=action, side=side, price=price, size=size, bid_px=bpx, bid_sz=bsz, ask_px=apx, ask_sz=asz, last=last, bad=bad)

print("== F10.7 QI1s hand tests (t = 10.0 s; ask fixed at 102 x 40 unless stated)")
base = [R(8.0, 'A', 'B', 100, 50, 100, 50, 102, 40)]
# 1. MathReview B1 counterexample: rise at 9.5 to 101, cancel at 9.8 back to 100
c1 = base + [R(9.5, 'A', 'B', 101, 5, 101, 5, 102, 40), R(9.8, 'C', 'B', 101, 5, 100, 50, 102, 40)]
print("1 rise-then-fall (B1): v0.2", qb_tilde_v02(c1, 10.0), "| v0.1", qb_tilde_v01(c1, 10.0), "| exact seasoned depth 50 (upper bound expected >= 50)")
# 2. pure rise inside the second
c2 = base + [R(9.5, 'A', 'B', 101, 5, 101, 5, 102, 40)]
print("2 pure rise:          v0.2", qb_tilde_v02(c2, 10.0), "| exact 0")
# 3. flicker at the same price (no price change)
c3 = base + [R(9.3, 'A', 'B', 100, 10, 100, 60, 102, 40), R(9.6, 'C', 'B', 100, 10, 100, 50, 102, 40)]
print("3 flicker same price: v0.2", qb_tilde_v02(c3, 10.0), "| exact 50")
# 4. rise, fall, rise again (last change an increase)
c4 = base + [R(9.2, 'A', 'B', 101, 5, 101, 5, 102, 40), R(9.5, 'C', 'B', 101, 5, 100, 50, 102, 40), R(9.8, 'A', 'B', 101, 7, 101, 7, 102, 40)]
print("4 rise-fall-rise:     v0.2", qb_tilde_v02(c4, 10.0), "| exact 0")
# 5. two rises then a fall to an intermediate level: 100 -> 101 (9.2) -> 102? use 100->101->103->101
c5 = base + [R(9.2, 'A', 'B', 101, 5, 101, 5, 102, 40), R(9.5, 'A', 'B', 101, 0, 101, 5, 102, 40)]
c5 = base + [R(9.2, 'A', 'B', 101, 5, 101, 5, 110, 40), R(9.5, 'A', 'B', 103, 9, 103, 9, 110, 40), R(9.8, 'C', 'B', 103, 9, 101, 5, 110, 40)]
print("5 rise-rise-fall:     v0.2", qb_tilde_v02(c5, 10.0), "| exact 0 (orders at 101 added at 9.2); proxy is an upper bound only")
# 6. ask side: fall inside the second -> 0
c6 = base + [R(9.5, 'A', 'A', 101, 3, 100, 50, 101, 3)]
print("6 ask fell (improve): v0.2 ask", qb_tilde_v02(c6, 10.0, 'ask'), "| exact 0")
# 7. fall then rise on the bid where the old level is consumed: 100 -> 99 (9.4) -> 100 (9.7) new orders
c7 = base + [R(9.4, 'T', 'A', 100, 50, 99, 30, 102, 40), R(9.7, 'A', 'B', 100, 12, 100, 12, 102, 40)]
print("7 fall then new rise: v0.2", qb_tilde_v02(c7, 10.0), "| exact 0")

print("\n== F10.9 removal count hand tests (bid side)")
# A. post-fill reduction on the T record itself, then a 3-lot cancel; one batch
A = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'T', 'A', 100, 12, 100, 8, 101, 10, last=False), R(2.0, 'C', 'B', 100, 3, 100, 5, 101, 10)]
print("A reduction on T:     v0.2", cb_v02(A)[0], "| v0.1", cb_v01(A), "| expected 3")
# B. reduction on a later M record, then the 3-lot cancel; one batch
B = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'T', 'A', 100, 12, 100, 20, 101, 10, last=False), R(2.0, 'M', 'B', 100, 8, 100, 8, 101, 10, last=False), R(2.0, 'C', 'B', 100, 3, 100, 5, 101, 10)]
print("B reduction on M:     v0.2", cb_v02(B)[0], "| v0.1", cb_v01(B), "| expected 3")
# B2. reduction carried on an F record (undocumented action) in the same batch
B2 = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'T', 'A', 100, 12, 100, 20, 101, 10, last=False), R(2.0, 'F', 'B', 100, 12, 100, 8, 101, 10, last=False), R(2.0, 'C', 'B', 100, 3, 100, 5, 101, 10)]
print("B2 reduction on F:    v0.2", cb_v02(B2)[0], "| v0.1", cb_v01(B2), "| expected 3")
# C. reduction in a LATER batch (the case M1 marks as not handled)
C = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'T', 'A', 100, 12, 100, 20, 101, 10), R(2.1, 'C', 'B', 100, 12, 100, 8, 101, 10)]
print("C reduction next batch: v0.2", cb_v02(C)[0], "| v0.1", cb_v01(C), "| true removals 0 (both forms count the fill as a cancel; disclosed as not handled)")
# D. level fully consumed by a trade; touch falls to 99
D = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'T', 'A', 100, 20, 99, 30, 101, 10)]
print("D level consumed:     v0.2", cb_v02(D)[0], "| expected 0")
# E. genuine cancel that empties the level (touch falls), no trade
E = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'C', 'B', 100, 20, 99, 30, 101, 10)]
print("E cancel empties:     v0.2", cb_v02(E)[0], "| expected 20")
# F. bad batch contributes 0
F = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'C', 'B', 100, 5, 100, 15, 101, 10, bad=True)]
print("F bad batch:          v0.2", cb_v02(F)[0], "| expected 0")
# G. partial fill then size increase then cancel in one batch: 20 -(T 12)-> 8 -(A 7)-> 15 -(C 4)-> 11
G = [R(1.0, 'A', 'B', 100, 20, 100, 20, 101, 10), R(2.0, 'T', 'A', 100, 12, 100, 8, 101, 10, last=False), R(2.0, 'A', 'B', 100, 7, 100, 15, 101, 10, last=False), R(2.0, 'C', 'B', 100, 4, 100, 11, 101, 10)]
print("G fill, add, cancel:  v0.2", cb_v02(G)[0], "| expected 4")
# H. touch rises within the batch then the new level is cancelled: 100x10 -> A 101x5 -> C 101 back to 100x10
H = [R(1.0, 'A', 'B', 100, 10, 100, 10, 102, 10), R(2.0, 'A', 'B', 101, 5, 101, 5, 102, 10, last=False), R(2.0, 'C', 'B', 101, 5, 100, 10, 102, 10)]
print("H rise then cancel:   v0.2", cb_v02(H)[0], "| expected 5")
