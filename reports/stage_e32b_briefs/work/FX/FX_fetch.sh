#!/usr/bin/env bash
# FX_fetch.sh <url> <outfile_basename> <note> : curl with browser headers into pages/FX, log sha256 + times.
set -u
URL="$1"; NAME="$2"; NOTE="${3:-}"
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/FX
OUT="$D/$NAME"
curl -sL --max-time 60 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' -o "$OUT" -w '%{http_code} %{content_type}\n' "$URL"
UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ'); PDT=$(TZ=America/Vancouver date '+%Y-%m-%d %H:%M:%S %Z')
SHA=$(sha256sum "$OUT" | cut -d' ' -f1); SZ=$(stat -c %s "$OUT")
if file "$OUT" | grep -q PDF; then pdftotext -layout "$OUT" "$OUT.txt" 2>/dev/null; echo "pdf -> $OUT.txt ($(wc -l < "$OUT.txt") lines)"; 
elif grep -qi '<html' "$OUT" 2>/dev/null; then python3 -I -c "import sys,html,re;t=open(sys.argv[1],errors='ignore').read();t=re.sub(r'(?is)<(script|style).*?</\1>','',t);t=re.sub(r'(?s)<[^>]+>','\n',t);t=html.unescape(t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[1]+'.txt','w').write(t)" "$OUT"; echo "html -> $OUT.txt ($(wc -l < "$OUT.txt") lines)"; fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$URL" "$UTC" "$PDT" "curl" "$SHA" "$NAME" "$NOTE size=$SZ" >> "$D/log.tsv"
echo "saved $NAME size=$SZ sha=$SHA"
