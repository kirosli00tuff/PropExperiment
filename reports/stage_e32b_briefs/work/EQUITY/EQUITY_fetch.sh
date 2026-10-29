#!/bin/bash
# EQUITY_fetch.sh URL FILENAME NOTE  -> saves raw page to pages/EQUITY/FILENAME, appends log.tsv row; pdf -> .txt too
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/EQUITY
LOG=$D/log.tsv
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
url="$1"; fn="$2"; note="${3:-}"
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
code=$(curl -sL -m 60 -o "$D/$fn" -w '%{http_code}' -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' "$url")
sha=$(sha256sum "$D/$fn" | cut -d' ' -f1); sz=$(stat -c%s "$D/$fn")
printf '%s\t%s\t%s\tcurl\t%s\t%s\thttp=%s size=%s %s\n' "$url" "$utc" "$pdt" "$sha" "$fn" "$code" "$sz" "$note" >> "$LOG"
if file "$D/$fn" | grep -q PDF; then pdftotext -layout "$D/$fn" "$D/$fn.txt" 2>/dev/null; fi
case "$fn" in *.html) python3 -I -c "
import re,sys,html
t=open(sys.argv[1],errors='ignore').read()
t=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',t); t=re.sub(r'(?s)<[^>]+>','\n',t); t=html.unescape(t)
t=re.sub(r'\n\s*\n+','\n',t); open(sys.argv[1]+'.txt','w').write(t)" "$D/$fn";; esac
echo "$code $sz $sha $fn"
