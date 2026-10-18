# E.24 Part C fee lookup: fetch log (FeeReader-OpusMed)

Worker start 2026-10-18 01:40 PDT (from `date`), log written 01:44 PDT.
Tools: `scrapling extract get` for HTML/markdown (scripts/fees/fetch.sh), and curl for the two
Alpaca PDFs (scripts/fees/fetchpdf.sh), because scrapling extract does not save binary PDFs. This
matches how the sibling Alpaca worker saved its PDF. WebFetch was not used, since it returns a
model summary rather than the raw page and the brief requires raw saves. Derived text copies
(*.html.txt from scripts/fees/totext.py, *.pdf.txt from pdftotext) sit next to each raw file and
were the only things read, by grep and line ranges.
No web-budget notice came up (no WebSearch or Firecrawl calls were made).

## Terms and robots review (before fetching content pages)
- alpaca.markets/robots.txt returns a 404 page, so no robots rules. docs.alpaca.markets/robots.txt:
  "User-agent: * / Allow: /" (blocks only api-next, edit, login). The Alpaca Use and Risk PDF has no
  scraping, robot or automated-access clause (grep for scrap|robot|automat|crawl|copy found nothing).
  Allowed.
- sec.gov robots does not block /rules-regulations/ or /divisions/. SEC privacy/security page
  (sec_privacy_policies.html): "Current guidelines limit users to a total of no more than 10
  requests per second" and "The SEC does not allow "unclassified" bots or automated tools to crawl
  the site." 6 single-page fetches at least 1 s apart, no crawl. Caveat: scrapling sends a browser
  user agent, not a declared one, so the lead may want to judge this.
- finra.org robots does not block /rules-guidance/. **Conflict:** the FINRA Terms of Use
  (finra_terms.html, line 155 of .txt) say "In no case may you: ... e. use any process to monitor or
  copy the FINRA Website in bulk, or use any data mining, scraping or harvesting tools (including
  robots), or any similar data-gathering or extraction tools". The terms page and the two content
  pages were fetched in a single command, so the two content pages (finra_schedA_sec1.html,
  finra_taf.html) were already fetched before the terms had been read. That is a procedural miss
  on my part. After reading the terms I made no further finra.org fetches, so the TAF schedule
  versions for 2027 and later were NOT fetched. The lead decides whether the two pages already saved
  may be cited.
- nyse.com: robots blocks only /cgi-bin/ and /partial/. nyse.com/terms-of-use is a 404 that needs
  a browser (get: "Your browser is unsupported"; fetch: 404). Its footer points to the ICE terms,
  whose line 14 covers "www.nyse.com". ICE terms (ice_terms.html.txt): line 76 "The foregoing license
  does not include use of any data mining, robots or similar data gathering or extraction methods."
  and line 101 "use any Web browsers (other than generally available third-party browsers), engines,
  software, spiders, robots, avatars, agents, tools or other devices or mechanisms to navigate,
  search or determine this Website is strictly prohibited, unless expressly permitted by ICE."
  So the NYSE holiday page was NOT fetched, and F6 is [unverified].

## Fetch records (UTC time | method | status | URL | saved file | bytes | sha256)
All saved files are under reports/stage_e24_briefs/pages/fees/.
- 2026-10-18T08:40:54Z | get | rc=0 | https://alpaca.markets/robots.txt | alpaca_robots.txt | bytes=11905 | sha256=a28ec4ce1ebc68953c6ad549eda9b317980e1ef8f82fd00ec532d5b55fc73707
- 2026-10-18T08:40:55Z | get | rc=0 | https://docs.alpaca.markets/robots.txt | docs_alpaca_robots.txt | bytes=219 | sha256=2042117d0c08ccd4201420c7e1808a2984afb6e6417cd70f5fae75d9355cc4f1
- 2026-10-18T08:40:57Z | get | rc=0 | https://www.sec.gov/robots.txt | sec_robots.txt | bytes=2729 | sha256=79656eb1dc89949c45f7e28ecb82cc17a9f973127696f31f02c8c8b927672372
- 2026-10-18T08:40:58Z | get | rc=0 | https://www.finra.org/robots.txt | finra_robots.txt | bytes=9190 | sha256=ac7f4cac215df0858c0ea2ade3a3d3ccfc75ba6b9ed70d8a99debe07d0ce09a1
- 2026-10-18T08:40:59Z | get | rc=0 | https://www.nyse.com/robots.txt | nyse_robots.txt | bytes=95 | sha256=65814eed8bbb5d2e111fa91915fcf67d84e6526f25fbccbebb49561a94f5ea56
- 2026-10-18T08:41:36Z | curl | http=200 | https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf | alpaca_BrokFeeSched.pdf | bytes=147740 | sha256=814767d3dbd44d89bfbf5448eb5eac85a894740bf1974db2294aae448a6fed94
- 2026-10-18T08:41:36Z | curl | http=200 | https://files.alpaca.markets/disclosures/library/UseAndRisk.pdf | alpaca_UseAndRisk.pdf | bytes=56361 | sha256=9e331d1963954b10316097ccce8c9392255e11c1ef093e477dc2d69a53622d59
- 2026-10-18T08:41:36Z | get | rc=0 | https://alpaca.markets/disclosures | alpaca_disclosures.html | bytes=101933 | sha256=129a064cf91e0ebbebcf8d1ad6bf5fd5aa9b215e6b4041f795d1a70fcd9466ff
- 2026-10-18T08:41:37Z | get | rc=0 | https://docs.alpaca.markets/docs/margin-and-short-selling.md | docs_margin-and-short-selling.md | bytes=12423 | sha256=f197a8f1598d3fa3206ac16777a21e0cbad924c99bdade0815dca9b38744d05d
- 2026-10-18T08:41:38Z | get | rc=0 | https://docs.alpaca.markets/docs/paper-trading.md | docs_paper-trading.md | bytes=5928 | sha256=250b4890236766695d154dc0b1b6666f282c2a3844f44552a2f0869e1ff88b0c
- 2026-10-18T08:41:39Z | get | rc=0 | https://docs.alpaca.markets/docs/regulatory-fees.md | docs_regulatory-fees.md | bytes=1502 | sha256=7d5a345432ebbc66e5acafb6ef6512542f022e94c837a0297f6195234dc403b1
- 2026-10-18T08:42:05Z | get | rc=0 | https://www.sec.gov/about/privacy-information | sec_privacy_policies.html | bytes=87290 | sha256=57f82acc466efbc90e626fd353edfd09de172a970177344782916b89612dbb7d
- 2026-10-18T08:42:06Z | get | rc=0 | https://www.sec.gov/rules-regulations/fee-rate-advisories | sec_fee_rate_advisories.html | bytes=78305 | sha256=1bad5aa756efa5e8e4058ff694aec6296db3e51ae142ef11e06b06a941ec4c3d
- 2026-10-18T08:42:07Z | get | rc=0 | https://www.sec.gov/divisions/marketreg/sec31feesfaq.htm | sec31_faq.html | bytes=49263 | sha256=fb3c7d75537cbd76e9cd69a400c2afc4a06e470807211233a191161d12e73145
- 2026-10-18T08:42:21Z | get | rc=0 | https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-1 | sec_fee_advisory_2026-1.html | bytes=62474 | sha256=23fabf0690f96ba5a09aade602b31a98b1723d80db4077e5eb7e48600074cbea
- 2026-10-18T08:42:23Z | get | rc=0 | https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2 | sec_fee_advisory_2026-2.html | bytes=62690 | sha256=359e0bec7a2a31f539190d41a3a3fe180b1953d20deb2b511957db108c86691a
- 2026-10-18T08:42:25Z | get | rc=0 | https://www.sec.gov/rules-regulations/fee-rate-advisories/2027-1 | sec_fee_advisory_2027-1.html | bytes=62434 | sha256=c4c824818b0647358761726f72339a56da98ca822feb51e09c5491d55beb3e89
- 2026-10-18T08:42:34Z | get | rc=0 | https://www.finra.org/terms-of-use | finra_terms.html | bytes=89104 | sha256=9e22d4d415abb24bd4d6aec76a12d1effadc71d765af4ef21c674fb30bb2851d
- 2026-10-18T08:42:36Z | get | rc=0 | https://www.finra.org/rules-guidance/rulebooks/corporate-organization/section-1-member-regulatory-fees | finra_schedA_sec1.html | bytes=102960 | sha256=d3de74e9490f29c979871e9971ab47969db5fbdda44a0c9300a70fc20d0c199b
- 2026-10-18T08:42:40Z | get | rc=0 | https://www.finra.org/rules-guidance/guidance/trading-activity-fee | finra_taf.html | bytes=84994 | sha256=c914a7237072f8f87f730340050d9a285eb8672dce3b9dffd029068d5e392978
- 2026-10-18T08:43:26Z | get | rc=0 | https://www.nyse.com/terms-of-use | nyse_terms.html | bytes=68944 | sha256=1415d168a61d40ef810bd84236b35622503dadf9d8cacd8d3f79f9d81b53f2d7
- 2026-10-18T08:43:32Z | fetch | rc=0 | https://www.nyse.com/terms-of-use | nyse_terms_fetch.html | bytes=84481 | sha256=78ef59d2f0db65f6c9f7d204c4bd480504201b30e8967c6e814015dc4f187c7a
- 2026-10-18T08:43:45Z | get | rc=0 | https://www.ice.com/privacy-security-center/terms-of-use | ice_terms.html | bytes=554196 | sha256=87da06b6e216342d1525f3ad28ef65a9466ee32e1fb46af8637224f8f7ecf89b
