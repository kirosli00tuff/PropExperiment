#!/usr/bin/env bash
# Usage: FIRMS_fetch.sh <url> <outfile_basename> <note> [method]
# Fetch one page with curl (browser headers), save raw under pages/FIRMS, extract text, log to log.tsv.
set -u
URL="$1"; OUT="$2"; NOTE="$3"; METHOD="${4:-curl}"
PAGES=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/FIRMS
LOG=$PAGES/log.tsv
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date '+%Y-%m-%d %H:%M:%S %Z')
CODE=$(curl -gsL --compressed --max-time 60 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' -o "$PAGES/$OUT" -w '%{http_code}' "$URL")
[ -f "$PAGES/$OUT" ] || { echo "FAILED $CODE $URL"; printf "%s\t%s\t%s\t%s (FAILED HTTP %s)\t-\t-\t%s\n" "$URL" "$UTC" "$PDT" "$METHOD" "$CODE" "$NOTE" >> "$LOG"; exit 1; }
SHA=$(sha256sum "$PAGES/$OUT" | cut -d' ' -f1)
SIZE=$(stat -c %s "$PAGES/$OUT")
python3 -I /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS/FIRMS_html2txt.py "$PAGES/$OUT" "$PAGES/$OUT.txt"
printf '%s\t%s\t%s\t%s (HTTP %s, %s bytes)\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "$METHOD" "$CODE" "$SIZE" "$SHA" "$OUT" "$NOTE" >> "$LOG"
echo "$CODE $SIZE $OUT $(wc -l < "$PAGES/$OUT.txt") lines"
