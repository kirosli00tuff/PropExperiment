"""Stage E.7 session cost: sum each assistant message's usage (deduplicated by message id) per transcript and model."""
import collections, glob, json, os
BASE = os.path.expanduser('~/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/99bb7678-38d8-413c-82c8-d103cf2d3163')
files = [(('lead', BASE + '.jsonl'))] + [(os.path.basename(p)[:-6], p) for p in sorted(glob.glob(BASE + '/subagents/**/*.jsonl', recursive=True))]
tot = collections.defaultdict(lambda: [0, 0, 0, 0])
for name, path in files:
    seen = {}
    first = last = None
    for line in open(path):
        try:
            o = json.loads(line)
        except Exception:
            continue
        m = o.get('message') or {}
        u = m.get('usage')
        if o.get('type') != 'assistant' or not u:
            continue
        mid = m.get('id') or o.get('uuid')
        seen[mid] = (m.get('model'), u)
        ts = o.get('timestamp')
        first = first or ts
        last = ts or last
    per = collections.defaultdict(lambda: [0, 0, 0, 0])
    for model, u in seen.values():
        v = [u.get('input_tokens', 0), u.get('output_tokens', 0), u.get('cache_read_input_tokens', 0), u.get('cache_creation_input_tokens', 0)]
        for i in range(4):
            per[model][i] += v[i]
            tot[model][i] += v[i]
    for model, v in per.items():
        print(f"{name} {model} first={first} last={last} in={v[0]} out={v[1]} cread={v[2]} ccreate={v[3]} total={sum(v)}")
print('| Model | Input | Output | Cache read | Cache creation | Total |')
print('|---|---|---|---|---|---|')
allv = [0, 0, 0, 0]
for model, v in sorted(tot.items()):
    print(f"| {model} | {v[0]:,} | {v[1]:,} | {v[2]:,} | {v[3]:,} | {sum(v):,} |")
    allv = [a + b for a, b in zip(allv, v)]
print(f"| all | {allv[0]:,} | {allv[1]:,} | {allv[2]:,} | {allv[3]:,} | {sum(allv):,} |")
