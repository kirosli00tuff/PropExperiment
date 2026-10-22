import ast, sys, pathlib
for d in sys.argv[1:]:
    for p in sorted(pathlib.Path(d).rglob('*.py')):
        if '__pycache__' in p.parts or 'tests' in p.parts: continue
        try:
            doc = ast.get_docstring(ast.parse(p.read_text())) or ''
        except Exception as e:
            doc = f'ERR {e}'
        line = doc.strip().split('\n')[0][:150] if doc else ''
        print(f'{p}: {line}')
