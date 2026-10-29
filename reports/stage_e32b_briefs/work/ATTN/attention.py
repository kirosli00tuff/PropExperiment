"""Stage E.32b B5 AttentionCounter: OpenAlex counts for spec section 3 D2 d.

Standalone extraction script. Reads OPENALEX_EMAIL from the repo .env inside the
process only (used as the mailto parameter of each request; never printed,
logged or written). No other .env value is read. Log lines carry the request
URL without the mailto parameter.

Outputs:
  reports/stage_e32b_briefs/F2_attention.json
  reports/stage_e32b_briefs/work/ATTN/attention_calls.log
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

os.nice(10)

REPO = "/home/kiros-li/Documents/GitHub/PropExperiment"
BRIEFS = os.path.join(REPO, "reports", "stage_e32b_briefs")
WORK = os.path.join(BRIEFS, "work", "ATTN")
OUT_JSON = os.path.join(BRIEFS, "F2_attention.json")
LOG_PATH = os.path.join(WORK, "attention_calls.log")
ENV_PATH = os.path.join(REPO, ".env")

API = "https://api.openalex.org/works"
MIN_GAP_S = 0.6
MAX_RETRIES = 2
RETRY_WAIT_S = 2.0
TIMEOUT_S = 30
ATTN_CLAUSE = (
    '(intraday OR "intra-day" OR "high-frequency" OR "high frequency" OR microstructure)'
)

# Spec section 9.1, copied exactly. Codes per the brief's B5 section.
UNDERLYINGS = [
    ("crude oil", "MCL QM CL", ['"crude oil futures"', '"WTI futures"']),
    ("natural gas", "MNG QG NG", ['"natural gas futures"']),
    ("gold", "MGC GC", ['"gold futures"']),
    ("silver", "SIL SI", ['"silver futures"']),
    ("copper", "MHG HG", ['"copper futures"']),
    ("euro", "M6E 6E", ['"euro FX futures"', '"EUR/USD futures"', '"euro currency futures"']),
    ("Australian dollar", "M6A 6A", ['"Australian dollar futures"', '"AUD/USD futures"']),
    ("bitcoin", "MBT BTC", ['"bitcoin futures"']),
    ("ether", "MET ETH", ['"ether futures"', '"ethereum futures"']),
    ("Nasdaq-100", "MNQ NQ", ['"Nasdaq-100 futures"', '"Nasdaq 100 futures"', '"E-mini Nasdaq"']),
    ("Russell 2000", "M2K RTY", ['"Russell 2000 futures"', '"E-mini Russell"']),
    ("Dow", "MYM YM", ['"Dow futures"', '"E-mini Dow"', '"DJIA futures"']),
    (
        "US Treasuries",
        "2YY 5YY 10Y 30Y ZT ZF ZN ZB",
        [
            '"Treasury futures"',
            '"Treasury note futures"',
            '"Treasury bond futures"',
            '"T-note futures"',
            '"T-bond futures"',
        ],
    ),
    ("corn", "MZC XC ZC", ['"corn futures"']),
    ("soybeans", "MZS XK ZS", ['"soybean futures"']),
    ("wheat", "MZW XW ZW", ['"wheat futures"']),
    ("soybean oil", "MZL ZL", ['"soybean oil futures"']),
    ("soybean meal", "MZM ZM", ['"soybean meal futures"']),
]


class SyntaxRejected(Exception):
    """Raised when OpenAlex rejects the query syntax; the run stops."""


def read_openalex_email():
    """Return OPENALEX_EMAIL from the repo .env without printing it."""
    with open(ENV_PATH, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if line.startswith("OPENALEX_EMAIL="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if not value:
                    raise RuntimeError("OPENALEX_EMAIL is empty in .env")
                return value
    raise RuntimeError("OPENALEX_EMAIL not found in .env")


def now_times():
    utc = datetime.now(timezone.utc)
    pdt = utc.astimezone(ZoneInfo("America/Vancouver"))
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ"), pdt.strftime("%Y-%m-%dT%H:%M:%S %Z")


def log_line(fh, text):
    fh.write(text + "\n")
    fh.flush()


def build_value(phrase_clause, with_attention):
    if with_attention:
        return f"({phrase_clause}) AND {ATTN_CLAUSE}"
    return f"({phrase_clause})"


def build_url(value):
    """URL without mailto, as logged."""
    return f"{API}?filter=title_and_abstract.search:{urllib.parse.quote(value, safe='')}&per-page=1"


def fetch_count(url_no_mail, email, log_fh):
    """One call with at most MAX_RETRIES retries on HTTP error. Returns a dict."""
    full_url = f"{url_no_mail}&mailto={urllib.parse.quote(email, safe='@')}"
    retries = 0
    while True:
        utc_s, pdt_s = now_times()
        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "PropExperiment-E32b-B5"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                status = resp.status
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            count = data["meta"]["count"]
            log_line(log_fh, f"{utc_s} | {pdt_s} | HTTP {status} | count={count} | retries={retries} | {url_no_mail}")
            return {"status": status, "count": count, "retries": retries, "fetched_utc": utc_s, "fetched_pdt": pdt_s}
        except urllib.error.HTTPError as err:
            log_line(log_fh, f"{utc_s} | {pdt_s} | HTTP {err.code} | error | retries={retries} | {url_no_mail}")
            if err.code == 400:
                raise SyntaxRejected(f"HTTP 400 on {url_no_mail}") from err
            if retries >= MAX_RETRIES:
                return {"status": err.code, "count": None, "retries": retries, "fetched_utc": utc_s, "fetched_pdt": pdt_s}
            retries += 1
            time.sleep(RETRY_WAIT_S)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as err:
            kind = type(err).__name__
            log_line(log_fh, f"{utc_s} | {pdt_s} | {kind} | retries={retries} | {url_no_mail}")
            if retries >= MAX_RETRIES:
                return {"status": kind, "count": None, "retries": retries, "fetched_utc": utc_s, "fetched_pdt": pdt_s}
            retries += 1
            time.sleep(RETRY_WAIT_S)


def main():
    os.makedirs(WORK, exist_ok=True)
    email = read_openalex_email()
    results = {}
    notes = []
    last_call = [0.0]

    def paced_fetch(url_no_mail, log_fh):
        gap = time.monotonic() - last_call[0]
        if last_call[0] and gap < MIN_GAP_S:
            time.sleep(MIN_GAP_S - gap)
        last_call[0] = time.monotonic()
        return fetch_count(url_no_mail, email, log_fh)

    with open(LOG_PATH, "a", encoding="utf-8") as log_fh:
        log_line(log_fh, f"# run start {now_times()[1]} | email not logged | 36 calls planned")
        try:
            for name, codes, phrases in UNDERLYINGS:
                phrase_clause = " OR ".join(phrases)
                full_value = build_value(phrase_clause, with_attention=True)
                diag_value = build_value(phrase_clause, with_attention=False)
                full = paced_fetch(build_url(full_value), log_fh)
                diag = paced_fetch(build_url(diag_value), log_fh)
                results[name] = {
                    "codes": codes,
                    "query_value": full_value,
                    "url_logged": build_url(full_value),
                    "diagnostic_query_value": diag_value,
                    "diagnostic_url_logged": build_url(diag_value),
                    "status": full["status"],
                    "count": full["count"],
                    "phrase_only_count": diag["count"],
                    "phrase_only_status": diag["status"],
                    "fetched_utc": full["fetched_utc"],
                    "fetched_pdt": full["fetched_pdt"],
                    "retries": full["retries"],
                    "phrase_only_retries": diag["retries"],
                }
                log_line(log_fh, f"# done {name}: count={full['count']} phrase_only={diag['count']}")
        except SyntaxRejected as err:
            notes.append(f"STOPPED: OpenAlex rejected query syntax ({err}). Query not changed. Run incomplete.")
            log_line(log_fh, f"# STOPPED {now_times()[1]}: {err}")

    out = {"underlyings": results, "notes": notes}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"underlyings written: {len(results)} of {len(UNDERLYINGS)}; notes: {len(notes)}")


if __name__ == "__main__":
    main()
