import sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET
url='http://export.arxiv.org/api/query?'+urllib.parse.urlencode({'id_list':sys.argv[1],'max_results':20})
d=urllib.request.urlopen(url,timeout=60).read()
ns={'a':'http://www.w3.org/2005/Atom'}
for e in ET.fromstring(d).findall('a:entry',ns):
    print('##',e.find('a:id',ns).text.split('/')[-1], ' '.join(e.find('a:title',ns).text.split()))
    print(' '.join(e.find('a:summary',ns).text.split())[:900])
