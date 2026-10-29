#!/usr/bin/env bash
# usage: GRAINS_fetch.sh <url> <outfile_basename> <note>
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/GRAINS
url="$1"; out="$P/$2"; note="${3:-}"
curl -sL --max-time 90 -o "$out" \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' -w '%{http_code}' "$url" > "$out.code"
code=$(cat "$out.code"); rm -f "$out.code"
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%z)
if [ ! -s "$out" ]; then echo "EMPTY http=$code"; rm -f "$out"; exit 1; fi
sha=$(sha256sum "$out" | cut -d' ' -f1)
ft=$(file -b "$out" | cut -c1-40)
case "$ft" in PDF*) pdftotext -layout "$out" "$out.txt" 2>/dev/null ;; HTML*|*text*) python3 -I -c "import sys,re,html;t=open(sys.argv[1],errors='ignore').read();t=re.sub(r'(?is)<(script|style).*?</\1>',' ',t);t=re.sub(r'<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'[ \t]+',' ',t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[1]+'.txt','w').write(t)" "$out" ;; esac
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "curl" "$sha" "$(basename $out)" "http=$code $ft; $note" >> $P/log.tsv
echo "OK http=$code $ft size=$(stat -c %s "$out") lines_txt=$( [ -f "$out.txt" ] && wc -l < "$out.txt" || echo 0)"
