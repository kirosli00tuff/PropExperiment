#!/bin/bash
# usage: a2tf_logwf.sh <url> <file> <note>   (file already written in pages dir)
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_tradeify
sha=$(sha256sum "$P/$2" | cut -c1-64)
printf "%s\t%s\t%s\tWebFetch (deviation fetch; model-extracted text, not raw HTML)\t%s\t%s\t%s\n" "$1" "$(date -u +%FT%TZ)" "$(TZ=America/Vancouver date +%FT%T%z)" "$sha" "$2" "$3" >> $P/log.tsv
echo "$2 deviation fetch $1 $(date -u +%FT%TZ)" >> $P/DO_NOT_COMMIT.txt
