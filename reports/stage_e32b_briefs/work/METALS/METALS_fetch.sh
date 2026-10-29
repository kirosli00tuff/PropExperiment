#!/usr/bin/env bash
# METALS_fetch.sh <url> <filename> <method:curl|scrapling-get|scrapling-fetch> <note>
# Saves a page raw under pages/METALS/, converts PDFs with pdftotext, logs URL, UTC and PDT times, sha256.
set -u
URL="$1"; NAME="$2"; METHOD="${3:-curl}"; NOTE="${4:-}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/METALS
OUT="$DIR/$NAME"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
case "$METHOD" in
  curl) curl -sL --max-time 90 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$OUT" "$URL"; RC=$? ;;
  scrapling-get) scrapling extract get "$URL" "$OUT" >/dev/null 2>&1; RC=$? ;;
  scrapling-fetch) scrapling extract fetch "$URL" "$OUT" >/dev/null 2>&1; RC=$? ;;
  *) echo "bad method"; exit 2 ;;
esac
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
if [ ! -s "$OUT" ]; then echo "FAIL rc=$RC empty"; printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "$METHOD" "-" "$NAME" "FAILED rc=$RC: $NOTE" >> "$DIR/log.tsv"; exit 1; fi
SHA=$(sha256sum "$OUT" | cut -d' ' -f1)
TYPE=$(file -b "$OUT" | cut -c1-40)
if echo "$TYPE" | grep -q PDF; then pdftotext -layout "$OUT" "$OUT.txt" 2>/dev/null; else python3 -I -c "
import re,sys,html
t=open(sys.argv[1],errors='ignore').read()
t=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',t); t=re.sub(r'(?s)<[^>]+>',' ',t); t=html.unescape(t)
t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
open(sys.argv[1]+'.txt','w').write(t)" "$OUT"; fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "$METHOD" "$SHA" "$NAME" "$NOTE" >> "$DIR/log.tsv"
echo "OK $TYPE size=$(stat -c%s "$OUT") txtlines=$(wc -l < "$OUT.txt") sha=$SHA utc=$UTC"
