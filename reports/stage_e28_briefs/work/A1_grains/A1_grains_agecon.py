"""A1_grains: for AgEcon record ids, open the record page in one stealthy browser session, find files/*.pdf, save the
first PDF as agecon_<id>.pdf, log sha256. usage: python A1_grains_agecon.py <id> [<id> ...]"""
import sys, re, hashlib, datetime, time
from zoneinfo import ZoneInfo
from scrapling.fetchers import StealthySession
D = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_grains/'
def log(url, out, body, code, how):
    sha = hashlib.sha256(body).hexdigest()
    utc = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    pdt = datetime.datetime.now(ZoneInfo('America/Vancouver')).strftime('%Y-%m-%dT%H:%M:%S%Z')
    open(D + 'log.tsv', 'a').write(f"{url}\t{utc}\t{pdt}\t{how}\t{sha}\t{out}\thttp={code} size={len(body)}\n")
with StealthySession(headless=True, network_idle=True, timeout=90000) as s:
    for rid in sys.argv[1:]:
        rec = f'https://ageconsearch.umn.edu/record/{rid}'
        p = s.fetch(rec, wait=5000)
        html = p.html_content if hasattr(p, 'html_content') else str(p.body)
        open(D + f'agecon_record_{rid}.html', 'w').write(html)
        log(rec, f'agecon_record_{rid}.html', html.encode(), p.status, 'scrapling stealthy session')
        links = sorted(set(re.findall(rf'/record/{rid}/files/[^"?\s]+\.pdf', html)))
        title = re.search(r'<title>(.*?)</title>', html, re.S)
        print(rid, (title.group(1).strip()[:120] if title else ''), links[:3])
        if not links:
            continue
        url = 'https://ageconsearch.umn.edu' + links[0]
        time.sleep(6)
        pg = s.context.new_page()
        try:
            r = pg.request.get(url, timeout=90000); body = r.body(); code = r.status
        finally:
            pg.close()
        out = f'agecon_{rid}.pdf'
        open(D + out, 'wb').write(body); log(url, out, body, code, 'scrapling stealthy session (request.get)')
        print('  saved', out, code, len(body), body[:5])
        time.sleep(6)
