#!/bin/bash
# usage: A2_platforms_fetch.sh <url> <outfile_basename> <method:curl|wayback> [note]
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_platforms
url="$1"; out="$2"; method="${3:-curl}"; note="${4:-}"
UA="${A2UA:-Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36}"
curl -sL --max-time 60 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$P/$out" -w '%{http_code} %{size_download}\n' "$url"
utc=$(date -u '+%FT%TZ'); pdt=$(TZ=America/Vancouver date '+%F %T %Z')
sha=$(sha256sum "$P/$out" | cut -d' ' -f1)
case "$out" in *.pdf) pdftotext -layout "$P/$out" "$P/$out.txt" 2>/dev/null;; *.html|*.htm) python3 -I -c "import sys,html,re;t=open(sys.argv[1],errors='ignore').read();t=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',t);t=re.sub(r'(?s)<br\s*/?>|</p>|</li>|</h[1-6]>|</tr>|</div>','\n',t);t=re.sub(r'(?s)<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'[ \t]+',' ',t);t=re.sub(r'\n\s*\n+','\n',t);open(sys.argv[1]+'.txt','w').write(t)" "$P/$out";; esac
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$method" "$sha" "$out" "$note" >> "$P/log.tsv"
wc -c "$P/$out" "$P/$out.txt" 2>/dev/null | head -2
