import sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET, time
q=sys.argv[1]; n=int(sys.argv[2]) if len(sys.argv)>2 else 10
url='http://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'start':0,'max_results':n})
d=urllib.request.urlopen(url,timeout=60).read()
ns={'a':'http://www.w3.org/2005/Atom'}
for e in ET.fromstring(d).findall('a:entry',ns):
    print(e.find('a:id',ns).text.split('/')[-1], e.find('a:published',ns).text[:10], ' '.join(e.find('a:title',ns).text.split())[:110])
