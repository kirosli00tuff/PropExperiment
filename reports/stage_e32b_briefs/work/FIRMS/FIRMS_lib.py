"""Helpers to build F2_firms.json entries with source metadata from pages/FIRMS/log.tsv."""
import json, os, csv
BASE = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs'
PAGES = BASE + '/pages/FIRMS'
OUT = BASE + '/F2_firms.json'
SPEC_SHA = '09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635'

def _log():
    rows = {}
    with open(PAGES + '/log.tsv') as fh:
        for r in csv.DictReader(fh, delimiter='\t'):
            if r['file'] and r['file'] != '-':
                rows[r['file']] = r  # last fetch wins
    return rows

LOG = _log()

def src(file, url=None):
    if file is None:
        return None
    if file.startswith('reports/'):  # reused earlier-stage file
        return {'file': file, 'url': url, 'fetched_utc': None, 'sha256': None}
    base = file
    for suf in ('.flat.txt', '.txt'):
        if file.endswith(suf) and file[:-len(suf)] in LOG:
            base = file[:-len(suf)]
            break
    r = LOG.get(base) or LOG.get(file)
    if r is None:
        raise KeyError(f'no log row for {file}')
    return {'file': 'reports/stage_e32b_briefs/pages/FIRMS/' + file, 'url': url or r['url'],
            'fetched_utc': r['utc_fetch'], 'sha256': r['sha256']}

def check_quote(file, quote):
    """Every ' ... '-separated piece of the quote must appear in the page text (whitespace-normalised)."""
    if file is None or quote is None or file.startswith('reports/'):
        return True
    path = PAGES + '/' + file
    txt = ' '.join(open(path, encoding='utf-8', errors='replace').read().replace('\u200b', ' ').split())
    for piece in quote.split(' ... '):
        p = ' '.join(piece.split())
        if p and p not in txt:
            raise ValueError(f'quote piece not found in {file}: {p[:120]}')
    return True

def E(value, quote, file, old_value=None, old_path=None, changed=False, verified=True, url=None, note=None, also=()):
    check_quote(file, quote)
    for q2, f2 in also:
        check_quote(f2, q2)
    e = {'value': value, 'old_value': old_value, 'old_path': old_path, 'changed': changed,
         'quote': quote, 'source': src(file, url), 'verified': verified}
    if also:
        e['also'] = [{'quote': q2, 'source': src(f2)} for q2, f2 in also]
    if note:
        e['note'] = note
    return e

def save_firm(name, fields, notices=(), gaps=()):
    if os.path.exists(OUT):
        d = json.load(open(OUT))
    else:
        d = {'spec_sha256': SPEC_SHA, 'stage': 'E.32b', 'worker': 'FirmRules-OpusHigh', 'firms': {}, 'notices': [], 'gaps': []}
    d['firms'][name] = fields
    d['notices'] = [n for n in d['notices'] if n.get('firm') != name] + [dict(n, firm=name) for n in notices]
    d['gaps'] = [g for g in d['gaps'] if g.get('firm') != name] + [dict(g, firm=name) for g in gaps]
    tmp = OUT + '.tmp'
    json.dump(d, open(tmp, 'w'), indent=1, ensure_ascii=False)
    os.replace(tmp, OUT)
    print('saved', name, len(fields), 'fields')
