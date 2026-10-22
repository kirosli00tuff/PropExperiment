#!/usr/bin/env bash
# A1_crude fetch helper: fetch URL with curl (browser headers), save raw, log sha256.
# usage: A1_crude_fetch.sh <url> <outname> [note]
set -u
URL="$1"; OUT="$2"; NOTE="${3:-}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_crude
LOG="$DIR/log.tsv"
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
code=$(curl -sL --max-time 90 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' -o "$DIR/$OUT" -w '%{http_code}' "$URL")
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
SZ=$(stat -c %s "$DIR/$OUT" 2>/dev/null || echo 0)
SHA=$(sha256sum "$DIR/$OUT" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\thttp=%s size=%s %s\n' "$URL" "$UTC" "$PDT" "$SHA" "$OUT" "$code" "$SZ" "$NOTE" >> "$LOG"
echo "http=$code size=$SZ file=$OUT"
case "$OUT" in *.pdf) pdftotext -layout "$DIR/$OUT" "$DIR/${OUT%.pdf}.txt" 2>/dev/null && echo "txt lines: $(wc -l < "$DIR/${OUT%.pdf}.txt")";; esac
