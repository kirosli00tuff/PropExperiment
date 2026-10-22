#!/bin/bash
# usage: a2tf_wb.sh <wayback-url> <outname> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_tradeify
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
sleep 4
code=$(curl -sL -A "$UA" -H 'Accept: text/html,application/xhtml+xml' -H 'Accept-Language: en-US,en;q=0.9' -o "$P/$2" -w "%{http_code} %{url_effective}" "$1")
sha=$(sha256sum "$P/$2" | cut -c1-64)
python3 -I -c "
import re,sys,html
t=open(sys.argv[1],errors='ignore').read()
t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
t=html.unescape(re.sub(r'<[^>]+>','\n',t))
t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
open(sys.argv[1]+'.txt','w').write(t)
" "$P/$2"
printf "%s\t%s\t%s\twayback(curl)\t%s\t%s\t%s; http=%s\n" "$1" "$(date -u +%FT%TZ)" "$(TZ=America/Vancouver date +%FT%T%z)" "$sha" "$2" "$3" "$code" >> $P/log.tsv
echo "$code $(wc -l < $P/$2.txt) lines"
