#!/usr/bin/env bash
# CRYPTO_fetch.sh <url> <outfile_basename> <note> [method]
# Fetches a URL with curl (browser headers) into pages/CRYPTO/, logs to log.tsv, makes .txt for PDFs/HTML.
set -u
URL="$1"; NAME="$2"; NOTE="${3:-}"; METHOD="${4:-curl}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/CRYPTO
LOG="$DIR/log.tsv"
[ -f "$LOG" ] || printf 'url\tfetched_utc\tfetched_pdt\tmethod\tsha256\tfile\tnote\n' > "$LOG"
OUT="$DIR/$NAME"
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
if [ "$METHOD" = "curl" ]; then
  CODE=$(curl -sL --max-time 90 -o "$OUT" -w '%{http_code}' \
    -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.9,*/*;q=0.8' \
    -H 'Accept-Language: en-US,en;q=0.9' "$URL")
elif [ "$METHOD" = "scrapling-get" ]; then
  scrapling extract get "$URL" "$OUT" >/dev/null 2>&1; CODE=$?
elif [ "$METHOD" = "scrapling-fetch" ]; then
  scrapling extract fetch "$URL" "$OUT" >/dev/null 2>&1; CODE=$?
fi
SIZE=$(stat -c %s "$OUT" 2>/dev/null || echo 0)
SHA=$(sha256sum "$OUT" 2>/dev/null | cut -d' ' -f1)
TYPE=$(file -b "$OUT" 2>/dev/null | cut -c1-30)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "$METHOD" "$SHA" "$NAME" "code=$CODE size=$SIZE type=$TYPE | $NOTE" >> "$LOG"
case "$TYPE" in
  PDF*) pdftotext -layout "$OUT" "$OUT.txt" 2>/dev/null ;;
  HTML*|*XML*|*text*) python3 -I -c 'import sys,html,re;t=open(sys.argv[1],errors="ignore").read();t=re.sub(r"(?is)<(script|style).*?</\1>"," ",t);t=re.sub(r"(?s)<[^>]+>","\n",t);t=html.unescape(t);t=re.sub(r"\n\s*\n+","\n",t);open(sys.argv[2],"w").write(t)' "$OUT" "$OUT.txt" ;;
esac
echo "code=$CODE size=$SIZE type=$TYPE sha=${SHA:0:12}"
