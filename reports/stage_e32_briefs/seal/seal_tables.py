"""Stage E.32 Part 0: tables for reports/stage_e32_test_seal.md from the seal manifest and file names only."""
import collections, glob, json, os, sys
sys.path.insert(0, ".")
import importlib.util
spec = importlib.util.spec_from_file_location("soy", "reports/stage_e32_briefs/seal/soy_test_seal.py")
soy = importlib.util.module_from_spec(spec); sys.modules["soy"] = soy; spec.loader.exec_module(soy)
m = json.load(open("docs/soy_test/SOY_TEST_MANIFEST.json"))
rows = sorted(m["raw_files"], key=lambda r: (r["kind"], r["root"], r["original_relpath"]))
with open("reports/stage_e32_briefs/seal/sealed_files_table.md", "w") as fh:
    fh.write("| # | Kind | Root | Path (repo-relative) | Span | Bytes | sha256 (plaintext) |\n|---|---|---|---|---|---|---|\n")
    for i, r in enumerate(rows, 1):
        fh.write(f"| {i} | {r['kind']} | {r['root']} | {r['original_relpath']} | {r['span']} | {r['bytes']:,} | {r['sha256_plaintext']} |\n")
print("rows", len(rows), "bytes", sum(r["bytes"] for r in rows))
print("by kind/root", dict(collections.Counter((r["kind"], r["root"]) for r in rows)))
# Plaintext ZM/ZS/ZL files kept, by class (names only).
L = soy.DEFAULT_LAYOUT
kept = collections.Counter()
for ds in sorted(glob.glob(str(L.glbx / "*" / "*"))):
    roots = soy._roots_in(os.path.basename(ds))
    if not roots: continue
    schema = os.path.basename(os.path.dirname(ds))
    for n in sorted(os.listdir(ds)):
        if n in ("manifest.json",): continue
        sp = soy.raw_span(n)
        if sp is None: kept[(schema, os.path.basename(ds), "unclassified")] += 1; continue
        cls = "before" if sp[1] <= soy.WINDOW_UTC[0] else ("2024-03+" if sp[0] >= __import__("datetime").datetime(2024,3,1,tzinfo=__import__("datetime").UTC) else "discovery 2020-12..2024-02" if sp[0] >= soy.WINDOW_UTC[1] else "IN WINDOW?!")
        kept[(schema, os.path.basename(ds), cls, sp[0].date().isoformat() if cls!="before" else "")] += 0
        kept[(schema, os.path.basename(ds), cls)] += 1
for k, v in sorted(kept.items()):
    if v: print("kept raw", k, v)
for root in soy.ROOTS:
    for pat in L.store_globs:
        for f in sorted(glob.glob(str(L.repo_root / pat.format(root=root)))):
            print("kept store", os.path.relpath(f, L.repo_root))
for f in sorted(glob.glob("data/vendor/databento/rolls/*")):
    if soy._roots_in(os.path.basename(f)): print("rolls", os.path.basename(f))
