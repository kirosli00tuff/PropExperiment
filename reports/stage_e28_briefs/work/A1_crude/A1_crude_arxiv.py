# arXiv API query; prints id, title. usage: python A1_crude_arxiv.py "<search_query>" ...
import sys, urllib.request, urllib.parse, re, time
for q in sys.argv[1:]:
    u='http://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'max_results':10})
    try: t=urllib.request.urlopen(u,timeout=60).read().decode()
    except Exception as e: print('ERR',q,e); continue
    print('##',q)
    for e in re.findall(r'<entry>(.*?)</entry>',t,re.S):
        i=re.search(r'<id>http://arxiv.org/abs/(.*?)</id>',e).group(1); ti=' '.join(re.search(r'<title>(.*?)</title>',e,re.S).group(1).split())
        print(' ',i,ti[:120])
    time.sleep(3)
