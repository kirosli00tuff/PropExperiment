"""A1_grains: fetch PDFs behind a JS WAF with scrapling StealthyFetcher (one browser session), save bytes, log sha256.
usage: python A1_grains_sfpdf.py <record_url> <pdf_url> <outname> [<pdf_url> <outname> ...]"""
import sys, hashlib, datetime, time, os
from zoneinfo import ZoneInfo
from scrapling.fetchers import StealthySession
D = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_grains/'
rec = sys.argv[1]; pairs = list(zip(sys.argv[2::2], sys.argv[3::2]))
with StealthySession(headless=True, network_idle=True, timeout=90000) as s:
    s.fetch(rec, wait=6000)
    for url, out in pairs:
        time.sleep(6)
        page = s.context.new_page() if hasattr(s, 'context') and s.context else None
        try:
            resp = page.request.get(url, timeout=90000)
            body = resp.body(); code = resp.status
        finally:
            page.close()
        open(D + out, 'wb').write(body)
        sha = hashlib.sha256(body).hexdigest()
        utc = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        pdt = datetime.datetime.now(ZoneInfo('America/Vancouver')).strftime('%Y-%m-%dT%H:%M:%S%Z')
        open(D + 'log.tsv', 'a').write(f"{url}\t{utc}\t{pdt}\tscrapling stealthy session (request.get)\t{sha}\t{out}\thttp={code} size={len(body)} head={body[:5]!r}\n")
        print(out, code, len(body), body[:5])
