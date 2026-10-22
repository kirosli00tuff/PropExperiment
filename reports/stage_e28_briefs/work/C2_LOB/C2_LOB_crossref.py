import json, sys, time, urllib.request, urllib.parse
dois = sys.argv[1].split(',')
titles = sys.argv[2].split('|')
def show(m):
    a = [x.get('family') for x in m.get('author', [])]
    print(m.get('DOI'), '|', (m.get('title') or [''])[0][:90], '|', (m.get('container-title') or [''])[0], '|',
          m.get('volume'), m.get('issue'), m.get('page'), '|', (m.get('issued', {}).get('date-parts') or [[None]])[0], '|', a[:4])
for d in dois:
    try:
        m = json.load(urllib.request.urlopen('https://api.crossref.org/works/' + urllib.parse.quote(d), timeout=30))['message']; show(m)
    except Exception as e:
        print(d, 'ERR', e)
    time.sleep(1)
for t in titles:
    q = urllib.parse.quote(t)
    try:
        items = json.load(urllib.request.urlopen(f'https://api.crossref.org/works?query.bibliographic={q}&rows=2', timeout=30))['message']['items']
        for m in items: show(m)
    except Exception as e:
        print(t, 'ERR', e)
    time.sleep(1)
