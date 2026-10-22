#!/usr/bin/env bash
# A2_topstep fetch helper: one curl request per URL, browser headers, raw save, sha256, log.tsv row, text extraction.
# Usage: A2_topstep_fetch.sh <url> <name> [note]
set -u
URL="$1"; NAME="$2"; NOTE="${3:-}"
ROOT=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs
PAGES="$ROOT/pages/A2_topstep"
WORK="$ROOT/work/A2_topstep"
LOG="$PAGES/log.tsv"
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
OUT="$PAGES/$NAME"
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PDT=$(TZ=America/Vancouver date '+%Y-%m-%d %H:%M:%S %Z')
CODE=$(curl -sL --compressed -o "$OUT" -w '%{http_code}' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' "$URL")
SHA=$(sha256sum "$OUT" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "curl (HTTP $CODE)" "$SHA" "$NAME" "$NOTE" >> "$LOG"
python3 -I "$WORK/A2_topstep_extract.py" "$OUT" "$OUT.txt" 2>/dev/null
echo "$CODE $(wc -c < "$OUT") bytes, txt $(wc -l < "$OUT.txt" 2>/dev/null) lines, sha ${SHA:0:12}"
sleep 3.5
