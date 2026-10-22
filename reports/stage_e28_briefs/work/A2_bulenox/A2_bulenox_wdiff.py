import difflib, sys
a = open(sys.argv[1]).read().split(); b = open(sys.argv[2]).read().split()
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != 'equal':
        print(f"[{op}] OLD: {' '.join(a[i1:i2])[:600]}\n        NEW: {' '.join(b[j1:j2])[:900]}")
