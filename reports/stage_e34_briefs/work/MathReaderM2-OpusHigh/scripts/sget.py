import sys
from scrapling.fetchers import Fetcher
url, out = sys.argv[1], sys.argv[2]
r = Fetcher.get(url, stealthy_headers=True, timeout=60, impersonate='chrome')
open(out, 'wb').write(r.body)
print(r.status, len(r.body))
