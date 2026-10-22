#!/bin/bash
curl -sL --max-time 60 "https://export.arxiv.org/api/query?search_query=$1&max_results=${2:-8}" | python3 -c "
import sys,re
t=sys.stdin.read()
for e in t.split('<entry>')[1:]:
  i=re.search(r'<id>(.*?)</id>',e).group(1); ti=' '.join(re.search(r'<title>(.*?)</title>',e,re.S).group(1).split()); d=re.search(r'<published>(.*?)</published>',e).group(1)[:10]
  print(i.split('/abs/')[1], d, ti[:120])"
sleep 3
