import ast, sys
for p in sys.argv[1:]:
    src = open(p).read()
    t = ast.parse(src)
    d = ast.get_docstring(t)
    print(f"===== {p} ({len(src.splitlines())} lines)")
    print(d if d else "(no module docstring)")
    for n in t.body:
        if isinstance(n, ast.Assign) and all(isinstance(x, ast.Name) and x.id.isupper() for x in n.targets):
            seg = ast.get_source_segment(src, n)
            if seg and len(seg) < 300:
                print("  CONST:", seg.replace("\n", " "))
        if isinstance(n, ast.ClassDef):
            cd = ast.get_docstring(n)
            print(f"  class {n.name}: {cd[:600] if cd else ''}")
