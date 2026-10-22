#!/bin/bash
# usage: A1_rates_fetch.sh <url> <outfile_basename> <note>
URL="$1"; OUT="$2"; NOTE="$3"
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_rates
LOG=$D/log.tsv
[ -f $LOG ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > $LOG
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
CODE=$(curl -sL --max-time 90 -o "$D/$OUT" -w '%{http_code}' \
 -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
 -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
 -H 'Accept-Language: en-US,en;q=0.9' "$URL")
SZ=$(stat -c %s "$D/$OUT" 2>/dev/null || echo 0)
SHA=$(sha256sum "$D/$OUT" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" curl "$SHA" "$OUT" "http=$CODE size=$SZ $NOTE" >> $LOG
case "$OUT" in
 *.pdf) pdftotext -layout "$D/$OUT" "$D/$OUT.txt" 2>/dev/null ;;
 *.html|*.htm) python3 -I -c "
import sys,re,html
t=open(sys.argv[1],errors='ignore').read()
t=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',t)
t=re.sub(r'(?s)<[^>]+>','\n',t); t=html.unescape(t)
t=re.sub(r'\n\s*\n+','\n',t)
open(sys.argv[1]+'.txt','w').write(t)" "$D/$OUT" ;;
esac
echo "$OUT http=$CODE size=$SZ"
