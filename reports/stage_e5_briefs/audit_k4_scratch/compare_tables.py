import importlib.util, sys, hashlib
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old = load("reports/stage_e5_briefs/audit_k4_scratch/_releases_head.py", "rel_old")
new = load("strategy/members/k4/_releases.py", "rel_new")
for t in ["WPSR", "API_DROPPED_WEEKS", "NGS_UNVERIFIED_IN_WINDOW", "FEDERAL_MONDAY_HOLIDAYS", "NYSE_NOT_FULL", "DROPPED_WPSR", "DROPPED_NGS", "RELEASE_CALENDAR_SHA256", "RELEASE_CHECK_SHA256", "RESEARCH_CHECK_WINDOW"]:
    print(f"{t}: identical={getattr(old,t)==getattr(new,t)} len_old={len(getattr(old,t))} len_new={len(getattr(new,t))}")
on, nn = old.NGS, new.NGS
print("NGS len old/new", len(on), len(nn))
removed = [r for r in on if r not in nn]; added = [r for r in nn if r not in on]
print("removed:", removed); print("added:", added)
print("order preserved:", [r for r in on if r in nn] == list(nn))
print("new DROPPED_NGS_CONFIRMATION dates:", [d for d,_ in new.DROPPED_NGS_CONFIRMATION])
print("removed dates == dropped dates:", [d for d,_ in removed] == [d for d,_ in new.DROPPED_NGS_CONFIRMATION])
print("new-only names:", sorted(set(new.__all__) - set(old.__all__)), "old-only names:", sorted(set(old.__all__) - set(new.__all__)))
print("all module-level names new-only:", sorted(set(n for n in dir(new) if not n.startswith('_')) - set(n for n in dir(old) if not n.startswith('_'))))
print("E5_NGS_CHECK_SHA256", new.E5_NGS_CHECK_SHA256, "CONF_WINDOW", new.CONFIRMATION_CHECK_WINDOW)
print("sha256(reports/stage_e5_ngs_check.json) =", hashlib.sha256(open("reports/stage_e5_ngs_check.json","rb").read()).hexdigest())
