import ast, sys
for p in sys.argv[1:]:
    d = ast.get_docstring(ast.parse(open(p).read())) or ""
    print("=====", p)
    print(d.split("SUPPORT CONDITION")[0].rstrip())
