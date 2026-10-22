import json, sys, re
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))['data']
out = []
def blocks_text(bl):
    res = []
    for b in bl or []:
        if b.get('text'): res.append(str(b['text']))
        if b.get('list'):
            for it in b['list']:
                res.append('- ' + (it if isinstance(it, str) else json.dumps(it, ensure_ascii=False)))
        for k, v in b.items():
            if k not in ('type', 'text', 'list') and v:
                res.append(f'[{k}] ' + (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
    return res
for it in d:
    for t in it.get('translations', []):
        if t.get('languages_code', '').startswith('en'):
            head = f"### id={it.get('id')} key={it.get('key','')} cat={it.get('category', it.get('group',''))} :: " + (t.get('title') or t.get('question') or '')
            out.append(head)
            if t.get('lead'): out.append(str(t['lead']))
            out += blocks_text(t.get('blocks'))
            out.append('')
txt = '\n'.join(out)
txt = re.sub(r'<[^>]+>', ' ', txt)
open(dst, 'w').write(txt)
print(len(d), len(txt.splitlines()))
