#!/usr/bin/env bash
# A2_lucid Wayback fetcher: usage A2_lucid_wb.sh <url> <outname> [note]
set -u
URL="$1"; OUT="$2"; NOTE="${3:-}"
DIR=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_lucid
LOG="$DIR/log.tsv"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
Q=$(echo "$URL" | sed 's#^https\?://##')
CDX=""
for i in 1 2 3; do
  CDX=$(curl -s -m 60 -A "$UA" "https://web.archive.org/cdx/search/cdx?url=${Q}&output=txt&filter=statuscode:200&fl=timestamp&limit=-1" | grep -E '^[0-9]{14}$' | tail -1)
  [ -n "$CDX" ] && break; sleep 5
done
if [ -z "$CDX" ]; then
  echo "NO_SNAPSHOT $URL"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$(date -u +%FT%TZ)" "$(TZ=America/Vancouver date +%FT%T%Z)" "wayback-cdx" "-" "-" "no 200 snapshot found; $NOTE" >> "$LOG"
  exit 0
fi
for i in 1 2 3; do
  sleep 3
  curl -s -L --compressed -m 120 -A "$UA" -H 'Accept: text/html,application/xhtml+xml' -H 'Accept-Language: en-US,en;q=0.9' "https://web.archive.org/web/${CDX}id_/${URL}" -o "$DIR/$OUT"
  [ -s "$DIR/$OUT" ] && break
done
if [ ! -s "$DIR/$OUT" ]; then
  echo "FETCH_FAIL $URL"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$(date -u +%FT%TZ)" "$(TZ=America/Vancouver date +%FT%T%Z)" "wayback snapshot ${CDX}" "-" "-" "fetch failed after 3 tries; $NOTE" >> "$LOG"
  rm -f "$DIR/$OUT"; exit 0
fi
SHA=$(sha256sum "$DIR/$OUT" | cut -c1-64)
SZ=$(stat -c %s "$DIR/$OUT")
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$(date -u +%FT%TZ)" "$(TZ=America/Vancouver date +%FT%T%Z)" "wayback snapshot ${CDX}" "$SHA" "$OUT" "size ${SZ}; $NOTE" >> "$LOG"
python3 -I -c "import sys,re,html;t=open(sys.argv[1],encoding='utf-8',errors='ignore').read();t=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',t);t=re.sub(r'(?i)<br\s*/?>|</p>|</li>|</h[1-6]>|</tr>|</div>','\n',t);t=re.sub(r'<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'[ \t]+',' ',t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[1]+'.txt','w').write(t)" "$DIR/$OUT"
echo "OK $CDX $SZ $OUT"
