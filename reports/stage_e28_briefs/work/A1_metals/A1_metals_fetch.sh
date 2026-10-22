#!/bin/bash
# usage: A1_metals_fetch.sh <url> <outname> [note]   (retries 3x; logs to log.tsv)
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_metals
url="$1"; out="$P/$2"; note="${3:-}"
for i in 1 2 3; do
 code=$(curl -sL --max-time 120 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
 -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" \
 -o "$out" -w "%{http_code}" "$url")
 if [ "$code" = "200" ]; then
   case "$out" in *.pdf) file -b "$out" | grep -q PDF && break ;; *) break ;; esac
 fi
 sleep $((i*5))
done
echo "HTTP $code"
[ -s "$out" ] || { echo FAIL; exit 1; }
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$out" | cut -d' ' -f1)
case "$out" in
 *.pdf) pdftotext -layout "$out" "${out%.pdf}.txt" 2>/dev/null ;;
 *.html|*.htm) python3 -I -c "import sys,re,html;t=open(sys.argv[1],errors='ignore').read();t=re.sub(r'(?s)<(script|style).*?</\1>',' ',t);t=re.sub(r'<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'[ \t]+',' ',t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[1]+'.txt','w').write(t)" "$out" ;;
esac
[ -f "$P/log.tsv" ] || printf "url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n" > "$P/log.tsv"
printf "%s\t%s\t%s\tcurl\t%s\t%s\t%s\n" "$url" "$utc" "$pdt" "$sha" "$2" "$note" >> "$P/log.tsv"
file -b "$out" | cut -c1-60
