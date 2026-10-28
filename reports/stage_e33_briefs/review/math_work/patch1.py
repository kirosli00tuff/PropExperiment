p="hand_replay.py"; s=open(p).read()
old_loop = """        # snapshot before applying a record later than the pending instant
        while inst_i < len(inst) and t > inst[inst_i]:
            snaps[inst[inst_i]] = _snapshot(book, otime, inst[inst_i], last_flast_ts)
            inst_i += 1
"""
new_loop = """        # the state as of an instant is the one after the last F_LAST record with ts_recv <=
        # instant (0.3), so snapshots are taken at F_LAST records (below), never from the live
        # book while a later event is half applied; here only advance past instants
        while inst_i < len(inst) and t > inst[inst_i]:
            if inst[inst_i] not in snaps:
                snaps[inst[inst_i]] = {"instant": inst[inst_i], "missing": True,
                                       "last_flast_ts": last_flast_ts}
            inst_i += 1
"""
assert old_loop in s; s = s.replace(old_loop, new_loop)
old_fl = """            batch_ts0 = None
            last_flast_ts = t
            u_ts.append(t)
"""
new_fl = """            batch_ts0 = None
            last_flast_ts = t
            if inst_i < len(inst) and t > inst[inst_i] - 30 * NS_SEC:
                snaps[inst[inst_i]] = _snapshot(book, otime, inst[inst_i], t)
            u_ts.append(t)
"""
assert old_fl in s; s = s.replace(old_fl, new_fl)
old_tail = """    while inst_i < len(inst):
        snaps[inst[inst_i]] = _snapshot(book, otime, inst[inst_i], last_flast_ts)
        inst_i += 1
"""
new_tail = """    while inst_i < len(inst):
        if inst[inst_i] not in snaps:
            snaps[inst[inst_i]] = {"instant": inst[inst_i], "missing": True,
                                   "last_flast_ts": last_flast_ts}
        inst_i += 1
"""
assert old_tail in s; s = s.replace(old_tail, new_tail)
open(p,"w").write(s)
p="hand_history.py"; s=open(p).read()
old = """    ofi_a, ofi_b, n_upd = window_sum_at_marks(u_ts, e, comp, vpair, mk)
"""
new = """    ofi_a, ofi_b, n_upd = window_sum_at_marks(u_ts, e, comp, vpair, mk)
    ofi5_a, ofi5_b, _ = window_sum_at_marks(u_ts, e, comp, vpair, mk, 5)
    ofi15_a, ofi15_b, _ = window_sum_at_marks(u_ts, e, comp, vpair, mk, 15)
"""
assert old in s; s = s.replace(old, new)
old = """           "mid_zm": mid, "depth": depth, "ofi_zm1_a": ofi_a, "ofi_zm1_b": ofi_b,
"""
new = """           "mid_zm": mid, "depth": depth, "ofi_zm1_a": ofi_a, "ofi_zm1_b": ofi_b,
           "ofi_zm5_a": ofi5_a, "ofi_zm5_b": ofi5_b, "ofi_zm15_a": ofi15_a, "ofi_zm15_b": ofi15_b,
"""
assert old in s; s = s.replace(old, new)
old = """            oa, ob, nu = window_sum_at_marks(ts, e2, c2, va[:-1] & va[1:], mk)
            out[f"mid_{root}_{tag}"] = mm
            out[f"ofi_{root}1_a_{tag}"] = oa
            out[f"ofi_{root}1_b_{tag}"] = ob
"""
new = """            oa, ob, nu = window_sum_at_marks(ts, e2, c2, va[:-1] & va[1:], mk)
            oa5, ob5, _ = window_sum_at_marks(ts, e2, c2, va[:-1] & va[1:], mk, 5)
            out[f"mid_{root}_{tag}"] = mm
            out[f"ofi_{root}1_a_{tag}"] = oa
            out[f"ofi_{root}1_b_{tag}"] = ob
            out[f"ofi_{root}5_a_{tag}"] = oa5
            out[f"ofi_{root}5_b_{tag}"] = ob5
"""
assert old in s; s = s.replace(old, new)
open(p,"w").write(s)
print("patched")
