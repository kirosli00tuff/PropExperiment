#!/bin/bash
# usage: M6_arxq.sh "<search_query>" [max]
curl -sL -m 40 "https://export.arxiv.org/api/query?search_query=$1&max_results=${2:-10}" -o M6_arx_tmp.xml
python3 - <<'PY'
import re
t=open('M6_arx_tmp.xml').read()
for e in t.split('<entry>')[1:]:
    i=re.search(r'<id>(.*?)</id>',e).group(1)
    ti=' '.join(re.search(r'<title>(.*?)</title>',e,re.S).group(1).split())
    y=re.search(r'<published>(\d{4})',e).group(1)
    print(i,'|',y,'|',ti[:110])
PY
