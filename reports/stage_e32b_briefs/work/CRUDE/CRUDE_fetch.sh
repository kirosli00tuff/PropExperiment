#!/usr/bin/env bash
# CRUDE_fetch.sh <url> <filename> <note> [method]
# Saves page raw under pages/CRUDE, converts PDFs with pdftotext, logs to log.tsv.
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/CRUDE
url="$1"; fn="$2"; note="${3:-}"; method="${4:-curl}"
out="$P/$fn"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
code=$(curl -sL --max-time 90 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$out" -w '%{http_code}' "$url")
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sz=$(stat -c %s "$out" 2>/dev/null || echo 0)
sha=$(sha256sum "$out" | cut -d' ' -f1)
if file "$out" | grep -q PDF; then pdftotext -layout "$out" "$out.txt" 2>/dev/null; kind=pdf; else
  python3 -I -c "import sys,re,html;t=open(sys.argv[1],errors='ignore').read();t=re.sub(r'(?is)<(script|style).*?</\1>',' ',t);t=re.sub(r'<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'[ \t]+',' ',t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[1]+'.txt','w').write(t)" "$out"; kind=html; fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$method" "$sha" "$fn" "http=$code size=$sz $kind; $note" >> "$P/log.tsv"
echo "http=$code size=$sz kind=$kind words=$(wc -w < "$out.txt" 2>/dev/null)"
