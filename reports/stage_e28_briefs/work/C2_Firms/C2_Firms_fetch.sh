#!/usr/bin/env bash
# C2_Firms_fetch.sh <url> <outfile_basename> [note]
# Fetch a page with curl (browser headers), save raw under pages/C2_Firms, log to log.tsv.
# For PDFs, also writes <file>.txt via pdftotext.
set -u
URL="$1"; NAME="$2"; NOTE="${3:-}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_Firms
LOG="$DIR/log.tsv"
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
OUT="$DIR/$NAME"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
CODE=$(curl -sL --max-time 60 -o "$OUT" -w '%{http_code}' \
  -H "User-Agent: $UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' "$URL")
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
SIZE=$(stat -c %s "$OUT" 2>/dev/null || echo 0)
if [ "$CODE" != "200" ] || [ "$SIZE" -lt 500 ]; then
  echo "FAIL http=$CODE size=$SIZE $URL"
  printf '%s\t%s\t%s\tcurl\t-\t-\tFAILED http=%s size=%s %s\n' "$URL" "$UTC" "$PDT" "$CODE" "$SIZE" "$NOTE" >> "$LOG"
  rm -f "$OUT"; exit 1
fi
SHA=$(sha256sum "$OUT" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "$SHA" "$NAME" "$NOTE" >> "$LOG"
if file "$OUT" | grep -q PDF; then pdftotext -layout "$OUT" "$OUT.txt" 2>/dev/null; echo "OK pdf $NAME $(wc -l < "$OUT.txt") lines"
else
  python3 -I -c 'import sys,re,html
t=open(sys.argv[1],encoding="utf-8",errors="ignore").read()
t=re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>"," ",t); t=re.sub(r"(?s)<[^>]+>","\n",t); t=html.unescape(t)
lines=[re.sub(r"\s+"," ",l).strip() for l in t.split("\n")]; lines=[l for l in lines if l]
open(sys.argv[1]+".txt","w").write("\n".join(lines))' "$OUT"
  echo "OK html $NAME $(wc -l < "$OUT.txt") lines"
fi
