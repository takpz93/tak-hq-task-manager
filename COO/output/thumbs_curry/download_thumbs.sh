#!/usr/bin/env bash
# 倍率上位30本のサムネ(maxresdefault)をこのディレクトリに保存する
cd "$(dirname "$0")"
while IFS=$'\t' read -r fn url; do
  [ -s "$fn" ] && continue
  curl -sSL -o "$fn" "$url" || curl -sSL -o "$fn" "${url/maxresdefault/hqdefault}"
  echo "saved $fn"
done < thumb_urls.txt
