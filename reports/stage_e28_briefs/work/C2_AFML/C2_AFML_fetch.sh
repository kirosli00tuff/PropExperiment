#!/usr/bin/env bash
# usage: C2_AFML_fetch.sh <url> <filename> <note>   (curl with browser headers; logs to pages/C2_AFML/log.tsv)
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_AFML
url="$1"; f="$2"; note="${3:-}"
curl -sL --max-time 120 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" \
  -o "$P/$f" "$url"
rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$P/$f" | cut -d' ' -f1); sz=$(stat -c%s "$P/$f")
typ=$(file -b "$P/$f" | cut -c1-30)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s (rc=%s,%sB,%s)\n' "$url" "$utc" "$pdt" "$sha" "$f" "$note" "$rc" "$sz" "$typ" >> "$P/log.tsv"
if [[ "$typ" == PDF* ]]; then pdftotext -layout "$P/$f" "$P/${f%.*}.txt" 2>/dev/null; echo "$f PDF ok $sz $(wc -l < "$P/${f%.*}.txt") lines"
elif [[ "$typ" == *HTML* || "$typ" == *XML* ]]; then python3 -c "import sys,re,html;t=open(sys.argv[1],errors='ignore').read();t=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',t);t=re.sub(r'(?s)<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'[ \t]+',' ',t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[2],'w').write(t)" "$P/$f" "$P/${f%.*}.txt"; echo "$f HTML $sz $(wc -l < "$P/${f%.*}.txt") lines"
else echo "$f rc=$rc $sz $typ"; fi
sleep 3
