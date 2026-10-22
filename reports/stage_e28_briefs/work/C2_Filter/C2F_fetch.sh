#!/usr/bin/env bash
# C2_Filter private fetch helper: C2F_fetch.sh <url> <file_name> <note>
# Saves raw page under pages/C2_Filter/, converts PDFs with pdftotext, strips HTML tags to .txt, logs to log.tsv.
set -u
URL="$1"; NAME="$2"; NOTE="${3:-}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_Filter
LOG="$DIR/log.tsv"
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
OUT="$DIR/$NAME"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
curl -sL --max-time 90 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/pdf,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' -o "$OUT" "$URL"
RC=$?
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
SIZE=$(stat -c %s "$OUT" 2>/dev/null || echo 0)
TYPE=$(file -b "$OUT" 2>/dev/null | cut -c1-40)
SHA=$(sha256sum "$OUT" 2>/dev/null | cut -d' ' -f1)
case "$TYPE" in
  PDF*) pdftotext -layout "$OUT" "${OUT%.*}.txt" 2>/dev/null ;;
  *HTML*|*XML*|*text*) python3 -I -c 'import re,sys,html;t=open(sys.argv[1],errors="ignore").read();t=re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>"," ",t);t=re.sub(r"<[^>]+>"," ",t);t=html.unescape(t);t=re.sub(r"[ \t]+"," ",t);t=re.sub(r"\n\s*\n+","\n",t);open(sys.argv[2],"w").write(t)' "$OUT" "$OUT.txt" ;;
esac
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "curl" "$SHA" "$NAME" "$NOTE (rc=$RC,${SIZE}B,$TYPE)" >> "$LOG"
echo "rc=$RC size=$SIZE type=$TYPE"
