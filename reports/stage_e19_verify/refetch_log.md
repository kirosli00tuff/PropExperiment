# Stage E.19 RulesReviewer spot re-fetch log

Method: curl, browser User-Agent, one request per named page, sleep 4 s before each (help.topstep.com robots.txt Crawl-delay 1), no link-following, no login, no API. Same method Task 1 used and the lead accepted in L-11; WebFetch was not used because it cannot save a raw copy with a sha256 for the diff. Times from date.

| URL | fetched UTC | fetched PDT | HTTP | file | sha256 |
|---|---|---|---|---|---|
| https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions | 2026-10-11 00:52:10Z | 2026-10-10 17:52:10 PDT | 200 | reports/stage_e19_verify/pages/art_14289835.html | ca17957542770461c4a9479b88596b40657202dd6c9d616a6296aa26d22ad2e3 |
| https://help.topstep.com/en/articles/8284233-topstep-payout-policy | 2026-10-11 00:52:15Z | 2026-10-10 17:52:15 PDT | 200 | reports/stage_e19_verify/pages/art_8284233.html | 9510b0979b4ee6b53b29531b78313f6d4b7eb6a0531be0b3eb0b9a38d5b418b6 |
| https://help.topstep.com/en/articles/8284215-express-funded-account-parameters | 2026-10-11 00:52:19Z | 2026-10-10 17:52:19 PDT | 200 | reports/stage_e19_verify/pages/art_8284215.html | 809abae10af05ba0ae9882fbd3eb7747503b8860ff33fff1d85a5fe880504c8a |
| https://help.topstep.com/en/articles/13747178-live-funded-account-call-up-and-call-down-process | 2026-10-11 00:52:24Z | 2026-10-10 17:52:24 PDT | 200 | reports/stage_e19_verify/pages/art_13747178.html | b214731489dd5ed0ceae276ea00dc0d7ec63b16dcd54e470de33766e77250017 |
| https://help.topstep.com/en/articles/10305426-prohibited-trading-strategies-at-topstep | 2026-10-11 00:52:28Z | 2026-10-10 17:52:28 PDT | 200 | reports/stage_e19_verify/pages/art_10305426.html | f96ffdc0ea4dbe6cf9fc606658ed817a645daccc6aa0786c3fc2484afe170888 |
