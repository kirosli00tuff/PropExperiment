#!/bin/bash
# usage: R3b_fetch.sh <url> <outfile_basename> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/R3b_microstructure
url="$1"; out="$P/$2"; note="$3"
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
code=$(curl -sL -m 90 -o "$out" -w "%{http_code}" \
 -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
 -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" \
 -H "Accept-Language: en-US,en;q=0.9" "$url")
sz=$(stat -c %s "$out" 2>/dev/null || echo 0)
sha=$(sha256sum "$out" 2>/dev/null | cut -d' ' -f1)
printf "%s\t%s\t%s\tcurl\t%s\t%s\thttp=%s size=%s %s\n" "$url" "$utc" "$pdt" "$sha" "$2" "$code" "$sz" "$note" >> "$P/log.tsv"
ftype=$(file -b "$out" | cut -c1-40)
if echo "$ftype" | grep -qi pdf; then pdftotext -layout "$out" "$out.txt" 2>/dev/null; echo "pdf pages: $(pdfinfo "$out" 2>/dev/null | grep Pages)"; fi
echo "$code $sz $ftype"
