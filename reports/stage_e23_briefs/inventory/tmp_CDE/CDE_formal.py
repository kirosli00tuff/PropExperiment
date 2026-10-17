import ast, sys, re
for p in sys.argv[1:]:
    src = open(p).read(); t = ast.parse(src); d = ast.get_docstring(t) or ""
    print(f"===== {p}")
    print(d.splitlines()[0] if d else "(none)")
    m = re.search(r"(Formali[sz]ation.*?)(?=SUPPORT CONDITION|\Z)", d, re.S)
    print(m.group(1) if m else "(no Formalization block)")
    for n in t.body:
        if isinstance(n, ast.Assign) and all(isinstance(x, ast.Name) and x.id.isupper() for x in n.targets):
            seg = ast.get_source_segment(src, n)
            if seg and len(seg) < 200: print("  CONST:", seg.replace("\n", " "))
