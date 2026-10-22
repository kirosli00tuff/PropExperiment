#!/bin/bash
# usage: A2_mffu_get.sh <url> <outname> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_mffu
url="$1"; out="$2"; note="$3"
code=$(curl -sL -o "$P/$out" -w '%{http_code}' --max-time 60 \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' "$url")
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%z)
sha=$(sha256sum "$P/$out" | cut -d' ' -f1); sz=$(stat -c %s "$P/$out")
[ -f "$P/log.tsv" ] || printf 'url\tutc\tpdt\tmethod\tsha256\tfile\tnote\n' > "$P/log.tsv"
printf '%s\t%s\t%s\tcurl\t%s\t%s\thttp=%s bytes=%s; %s\n' "$url" "$utc" "$pdt" "$sha" "$out" "$code" "$sz" "$note" >> "$P/log.tsv"
# text version
python3 -I -c '
import sys,re,html
s=open(sys.argv[1],encoding="utf-8",errors="replace").read()
s=re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>"," ",s)
s=re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr|td|th)>","\n",s)
s=re.sub(r"<[^>]+>"," ",s); s=html.unescape(s)
lines=[re.sub(r"[ \t]+"," ",l).strip() for l in s.split("\n")]
open(sys.argv[1]+".txt","w").write("\n".join(l for l in lines if l))
' "$P/$out"
echo "$code $sz $(wc -l < "$P/$out.txt")"
